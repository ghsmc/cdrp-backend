from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash
from datetime import timedelta
from app import db
from app.models import User, UserRole
from app.validators import (
    UserRegistrationSchema, UserLoginSchema, 
    PasswordResetSchema, PasswordChangeSchema,
    validate_request_data, validate_email_format
)
from app.permissions import log_audit_action, get_current_user

auth_bp = Blueprint('auth', __name__)

# In-memory blacklist for demo - use Redis in production
blacklisted_tokens = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    validated_data, errors = validate_request_data(UserRegistrationSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    if User.query.filter_by(username=validated_data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    if User.query.filter_by(email=validated_data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409
    
    user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        role=UserRole(validated_data['role']),
        region_id=validated_data.get('region_id')
    )
    user.set_password(validated_data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        log_audit_action('CREATE', 'USER', user.id, f'User {user.username} registered')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    validated_data, errors = validate_request_data(UserLoginSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    user = User.query.filter_by(username=validated_data['username']).first()
    
    if not user or not user.check_password(validated_data['password']):
        log_audit_action('FAILED_LOGIN', 'USER', None, f'Failed login attempt for {validated_data["username"]}')
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    log_audit_action('LOGIN', 'USER', user.id, f'User {user.username} logged in')
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'User not found or inactive'}), 404
    
    new_token = create_access_token(identity=str(current_user_id))
    
    return jsonify({
        'access_token': new_token
    }), 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    
    user = get_current_user()
    if user:
        log_audit_action('LOGOUT', 'USER', user.id, f'User {user.username} logged out')
    
    return jsonify({'message': 'Successfully logged out'}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Users can only update their own basic info
    allowed_fields = ['email', 'first_name', 'last_name']
    
    for field in allowed_fields:
        if field in data:
            if field == 'email':
                if not validate_email_format(data[field]):
                    return jsonify({'message': 'Invalid email format'}), 400
                
                existing_user = User.query.filter_by(email=data[field]).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({'message': 'Email already exists'}), 409
            
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        log_audit_action('UPDATE', 'USER', user.id, f'User {user.username} updated profile')
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    validated_data, errors = validate_request_data(PasswordChangeSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    if not user.check_password(validated_data['current_password']):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    user.set_password(validated_data['new_password'])
    
    try:
        db.session.commit()
        log_audit_action('CHANGE_PASSWORD', 'USER', user.id, f'User {user.username} changed password')
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Password change failed', 'error': str(e)}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    validated_data, errors = validate_request_data(PasswordResetSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    user = User.query.filter_by(email=validated_data['email']).first()
    
    # Always return success for security (don't reveal if email exists)
    if user:
        # TODO: Implement email sending with reset token
        # For now, just log the action
        log_audit_action('PASSWORD_RESET_REQUEST', 'USER', user.id, f'Password reset requested for {user.email}')
    
    return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200


# JWT token blacklist checker
@auth_bp.before_app_request
def check_if_token_revoked():
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    from flask import g
    
    try:
        verify_jwt_in_request(optional=True)
        jti = get_jwt().get('jti') if get_jwt() else None
        if jti and jti in blacklisted_tokens:
            return jsonify({'message': 'Token has been revoked'}), 401
    except Exception:
        pass