from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import User, UserRole


def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(int(current_user_id))
            
            if not user or not user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 404
            
            if user.role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_region_access(allow_admin=True):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(int(current_user_id))
            
            if not user or not user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 404
            
            if allow_admin and user.role == UserRole.ADMIN:
                return f(*args, **kwargs)
            
            region_id = request.view_args.get('region_id') or request.json.get('region_id') if request.json else None
            
            if region_id and user.region_id != region_id:
                return jsonify({'message': 'Access denied to this region'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return require_role(UserRole.ADMIN)(f)


def coordinator_required(f):
    return require_role(UserRole.ADMIN, UserRole.REGIONAL_COORDINATOR)(f)


def field_agent_required(f):
    return require_role(UserRole.ADMIN, UserRole.REGIONAL_COORDINATOR, UserRole.FIELD_AGENT)(f)


def get_current_user():
    current_user_id = get_jwt_identity()
    if current_user_id:
        return User.query.get(int(current_user_id))
    return None


def log_audit_action(action, resource_type, resource_id=None, details=None):
    from app.models import AuditLog
    from app import db
    
    user = get_current_user()
    if user:
        audit_log = AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging audit action: {e}")