from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timezone
from app import db, limiter
from app.models import (
    ReliefRequest, User, Region, DisasterType, AuditLog,
    RequestStatus, DisasterSeverity, UserRole
)
from app.validators import (
    ReliefRequestSchema, ReliefRequestUpdateSchema,
    RegionSchema, DisasterTypeSchema, SearchSchema,
    validate_request_data
)
from app.permissions import (
    admin_required, coordinator_required, field_agent_required,
    require_region_access, get_current_user, log_audit_action
)
from app.external_apis import DisasterDataIntegrator

api_bp = Blueprint('api', __name__)


# Relief Request endpoints
@api_bp.route('/requests', methods=['GET'])
@jwt_required()
@limiter.limit("50 per minute")
def get_relief_requests():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Parse query parameters
    args = request.args.to_dict()
    validated_data, errors = validate_request_data(SearchSchema, args)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    query = ReliefRequest.query
    
    # Apply filters based on user role and region
    if user.role not in [UserRole.ADMIN]:
        if user.region_id:
            query = query.filter(ReliefRequest.region_id == user.region_id)
    
    # Apply search filters
    if validated_data.get('query'):
        search_term = f"%{validated_data['query']}%"
        query = query.filter(or_(
            ReliefRequest.title.ilike(search_term),
            ReliefRequest.description.ilike(search_term),
            ReliefRequest.location.ilike(search_term)
        ))
    
    if validated_data.get('region_id'):
        query = query.filter(ReliefRequest.region_id == validated_data['region_id'])
    
    if validated_data.get('disaster_type_id'):
        query = query.filter(ReliefRequest.disaster_type_id == validated_data['disaster_type_id'])
    
    if validated_data.get('severity'):
        query = query.filter(ReliefRequest.severity == DisasterSeverity(validated_data['severity']))
    
    if validated_data.get('status'):
        query = query.filter(ReliefRequest.status == RequestStatus(validated_data['status']))
    
    if validated_data.get('created_by'):
        query = query.filter(ReliefRequest.created_by == validated_data['created_by'])
    
    if validated_data.get('assigned_to'):
        query = query.filter(ReliefRequest.assigned_to == validated_data['assigned_to'])
    
    if validated_data.get('date_from'):
        query = query.filter(ReliefRequest.created_at >= validated_data['date_from'])
    
    if validated_data.get('date_to'):
        query = query.filter(ReliefRequest.created_at <= validated_data['date_to'])
    
    # Apply sorting
    sort_column = getattr(ReliefRequest, validated_data['sort_by'])
    if validated_data['sort_order'] == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Paginate results
    page = validated_data['page']
    per_page = validated_data['per_page']
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    requests = [req.to_dict() for req in pagination.items]
    
    return jsonify({
        'requests': requests,
        'pagination': {
            'page': page,
            'pages': pagination.pages,
            'per_page': per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@api_bp.route('/requests', methods=['POST'])
@jwt_required()
@field_agent_required
@limiter.limit("10 per minute")
def create_relief_request():
    user = get_current_user()
    data = request.get_json()
    
    validated_data, errors = validate_request_data(ReliefRequestSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    # Check if disaster type exists
    disaster_type = DisasterType.query.get(validated_data['disaster_type_id'])
    if not disaster_type or not disaster_type.is_active:
        return jsonify({'message': 'Invalid disaster type'}), 400
    
    # Check if region exists
    region = Region.query.get(validated_data['region_id'])
    if not region or not region.is_active:
        return jsonify({'message': 'Invalid region'}), 400
    
    # Check region access for non-admin users
    if user.role != UserRole.ADMIN and user.region_id != validated_data['region_id']:
        return jsonify({'message': 'Access denied to this region'}), 403
    
    relief_request = ReliefRequest(
        title=validated_data['title'],
        description=validated_data['description'],
        location=validated_data['location'],
        coordinates=validated_data.get('coordinates'),
        severity=DisasterSeverity(validated_data['severity']),
        disaster_type_id=validated_data['disaster_type_id'],
        region_id=validated_data['region_id'],
        created_by=user.id,
        affected_population=validated_data.get('affected_population'),
        estimated_damage=validated_data.get('estimated_damage'),
        required_resources=validated_data.get('required_resources'),
        contact_person=validated_data.get('contact_person'),
        contact_phone=validated_data.get('contact_phone'),
        contact_email=validated_data.get('contact_email')
    )
    
    try:
        db.session.add(relief_request)
        db.session.commit()
        
        log_audit_action('CREATE', 'RELIEF_REQUEST', relief_request.id, 
                        f'Created relief request: {relief_request.title}')
        
        return jsonify({
            'message': 'Relief request created successfully',
            'request': relief_request.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Creation failed', 'error': str(e)}), 500


@api_bp.route('/requests/<int:request_id>', methods=['GET'])
@jwt_required()
def get_relief_request(request_id):
    user = get_current_user()
    relief_request = ReliefRequest.query.get_or_404(request_id)
    
    # Check region access for non-admin users
    if user.role != UserRole.ADMIN and user.region_id != relief_request.region_id:
        return jsonify({'message': 'Access denied to this region'}), 403
    
    return jsonify({'request': relief_request.to_dict()}), 200


@api_bp.route('/requests/<int:request_id>', methods=['PUT'])
@jwt_required()
@field_agent_required
def update_relief_request(request_id):
    user = get_current_user()
    relief_request = ReliefRequest.query.get_or_404(request_id)
    
    # Check permissions
    if (user.role not in [UserRole.ADMIN, UserRole.REGIONAL_COORDINATOR] and 
        relief_request.created_by != user.id):
        return jsonify({'message': 'Permission denied'}), 403
    
    data = request.get_json()
    validated_data, errors = validate_request_data(ReliefRequestUpdateSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    # Update fields
    update_fields = [
        'title', 'description', 'location', 'coordinates', 'severity',
        'disaster_type_id', 'region_id', 'affected_population', 
        'estimated_damage', 'required_resources', 'contact_person',
        'contact_phone', 'contact_email'
    ]
    
    changes = []
    for field in update_fields:
        if field in validated_data:
            if field == 'severity':
                new_value = DisasterSeverity(validated_data[field])
            else:
                new_value = validated_data[field]
            
            old_value = getattr(relief_request, field)
            if old_value != new_value:
                setattr(relief_request, field, new_value)
                changes.append(f'{field}: {old_value} -> {new_value}')
    
    # Handle status updates (only coordinators and admins)
    if 'status' in validated_data:
        if user.role in [UserRole.ADMIN, UserRole.REGIONAL_COORDINATOR]:
            new_status = RequestStatus(validated_data['status'])
            if relief_request.status != new_status:
                old_status = relief_request.status
                relief_request.status = new_status
                changes.append(f'status: {old_status.value} -> {new_status.value}')
                
                if new_status in [RequestStatus.COMPLETED, RequestStatus.REJECTED]:
                    relief_request.resolved_at = datetime.now(timezone.utc)
        else:
            return jsonify({'message': 'Permission denied to update status'}), 403
    
    # Handle assignment (only coordinators and admins)
    if 'assigned_to' in validated_data:
        if user.role in [UserRole.ADMIN, UserRole.REGIONAL_COORDINATOR]:
            relief_request.assigned_to = validated_data['assigned_to']
            changes.append(f'assigned_to: {validated_data["assigned_to"]}')
        else:
            return jsonify({'message': 'Permission denied to assign requests'}), 403
    
    try:
        db.session.commit()
        
        if changes:
            log_audit_action('UPDATE', 'RELIEF_REQUEST', relief_request.id,
                           f'Updated relief request: {", ".join(changes)}')
        
        return jsonify({
            'message': 'Relief request updated successfully',
            'request': relief_request.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Update failed', 'error': str(e)}), 500


@api_bp.route('/requests/<int:request_id>', methods=['DELETE'])
@jwt_required()
@coordinator_required
def delete_relief_request(request_id):
    relief_request = ReliefRequest.query.get_or_404(request_id)
    
    try:
        db.session.delete(relief_request)
        db.session.commit()
        
        log_audit_action('DELETE', 'RELIEF_REQUEST', request_id,
                        f'Deleted relief request: {relief_request.title}')
        
        return jsonify({'message': 'Relief request deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Deletion failed', 'error': str(e)}), 500


# Region endpoints
@api_bp.route('/regions', methods=['GET'])
@jwt_required()
def get_regions():
    regions = Region.query.filter_by(is_active=True).all()
    return jsonify({
        'regions': [region.to_dict() for region in regions]
    }), 200


@api_bp.route('/regions', methods=['POST'])
@jwt_required()
@admin_required
def create_region():
    data = request.get_json()
    
    validated_data, errors = validate_request_data(RegionSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    if Region.query.filter_by(name=validated_data['name']).first():
        return jsonify({'message': 'Region name already exists'}), 409
    
    if Region.query.filter_by(code=validated_data['code']).first():
        return jsonify({'message': 'Region code already exists'}), 409
    
    region = Region(**validated_data)
    
    try:
        db.session.add(region)
        db.session.commit()
        
        log_audit_action('CREATE', 'REGION', region.id, f'Created region: {region.name}')
        
        return jsonify({
            'message': 'Region created successfully',
            'region': region.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Creation failed', 'error': str(e)}), 500


# Disaster Type endpoints
@api_bp.route('/disaster-types', methods=['GET'])
@jwt_required()
def get_disaster_types():
    disaster_types = DisasterType.query.filter_by(is_active=True).all()
    return jsonify({
        'disaster_types': [dt.to_dict() for dt in disaster_types]
    }), 200


@api_bp.route('/disaster-types', methods=['POST'])
@jwt_required()
@admin_required
def create_disaster_type():
    data = request.get_json()
    
    validated_data, errors = validate_request_data(DisasterTypeSchema, data)
    if errors:
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    if DisasterType.query.filter_by(name=validated_data['name']).first():
        return jsonify({'message': 'Disaster type name already exists'}), 409
    
    if DisasterType.query.filter_by(code=validated_data['code']).first():
        return jsonify({'message': 'Disaster type code already exists'}), 409
    
    disaster_type = DisasterType(**validated_data)
    
    try:
        db.session.add(disaster_type)
        db.session.commit()
        
        log_audit_action('CREATE', 'DISASTER_TYPE', disaster_type.id, 
                        f'Created disaster type: {disaster_type.name}')
        
        return jsonify({
            'message': 'Disaster type created successfully',
            'disaster_type': disaster_type.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Creation failed', 'error': str(e)}), 500


# Analytics endpoints
@api_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@coordinator_required
def get_dashboard_analytics():
    user = get_current_user()
    
    # Base query with region filtering for non-admin users
    base_query = ReliefRequest.query
    if user.role != UserRole.ADMIN and user.region_id:
        base_query = base_query.filter(ReliefRequest.region_id == user.region_id)
    
    # Get counts by status
    status_counts = {}
    for status in RequestStatus:
        count = base_query.filter(ReliefRequest.status == status).count()
        status_counts[status.value] = count
    
    # Get counts by severity
    severity_counts = {}
    for severity in DisasterSeverity:
        count = base_query.filter(ReliefRequest.severity == severity).count()
        severity_counts[severity.value] = count
    
    # Get recent requests
    recent_requests = (base_query
                      .order_by(desc(ReliefRequest.created_at))
                      .limit(10)
                      .all())
    
    # Get requests by region (for admins)
    region_counts = {}
    if user.role == UserRole.ADMIN:
        regions = Region.query.filter_by(is_active=True).all()
        for region in regions:
            count = ReliefRequest.query.filter(ReliefRequest.region_id == region.id).count()
            region_counts[region.name] = count
    
    return jsonify({
        'status_counts': status_counts,
        'severity_counts': severity_counts,
        'region_counts': region_counts if user.role == UserRole.ADMIN else {},
        'recent_requests': [req.to_dict() for req in recent_requests],
        'total_requests': base_query.count()
    }), 200


# User management endpoints (admin only)
@api_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200


@api_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@admin_required
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    pagination = (AuditLog.query
                  .order_by(desc(AuditLog.timestamp))
                  .paginate(page=page, per_page=per_page, error_out=False))
    
    logs = [log.to_dict() for log in pagination.items]
    
    return jsonify({
        'logs': logs,
        'pagination': {
            'page': page,
            'pages': pagination.pages,
            'per_page': per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


# External Data Integration endpoints
@api_bp.route('/data/import/earthquakes', methods=['POST'])
@jwt_required()
@coordinator_required
@limiter.limit("5 per hour")
def import_earthquake_data():
    """Import recent earthquake data from USGS API"""
    user = get_current_user()
    
    # Get parameters
    data = request.get_json() or {}
    min_magnitude = data.get('min_magnitude', 4.0)
    
    try:
        imported_count = DisasterDataIntegrator.import_earthquake_data(min_magnitude)
        
        log_audit_action('IMPORT', 'EARTHQUAKE_DATA', None, 
                        f'Imported {imported_count} earthquake alerts (min_magnitude: {min_magnitude})')
        
        return jsonify({
            'message': f'Successfully imported {imported_count} earthquake alerts',
            'imported_count': imported_count,
            'min_magnitude': min_magnitude
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to import earthquake data',
            'error': str(e)
        }), 500


@api_bp.route('/data/import/weather-alerts', methods=['POST'])
@jwt_required()
@coordinator_required
@limiter.limit("5 per hour")
def import_weather_alerts():
    """Import active weather alerts from NOAA API"""
    user = get_current_user()
    
    # Get parameters
    data = request.get_json() or {}
    area = data.get('area', None)  # Optional state code like 'CA'
    
    try:
        imported_count = DisasterDataIntegrator.import_weather_alerts(area)
        
        log_audit_action('IMPORT', 'WEATHER_ALERTS', None, 
                        f'Imported {imported_count} weather alerts (area: {area or "all"})')
        
        return jsonify({
            'message': f'Successfully imported {imported_count} weather alerts',
            'imported_count': imported_count,
            'area': area or 'all'
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Failed to import weather alert data',
            'error': str(e)
        }), 500


@api_bp.route('/data/import/all', methods=['POST'])
@jwt_required()
@coordinator_required
@limiter.limit("3 per hour")
def import_all_disaster_data():
    """Import data from all external disaster APIs"""
    user = get_current_user()
    
    # Get parameters
    data = request.get_json() or {}
    min_magnitude = data.get('min_magnitude', 4.0)
    area = data.get('area', None)
    
    results = {
        'earthquakes': 0,
        'weather_alerts': 0,
        'errors': []
    }
    
    # Import earthquakes
    try:
        results['earthquakes'] = DisasterDataIntegrator.import_earthquake_data(min_magnitude)
    except Exception as e:
        results['errors'].append(f'Earthquake import failed: {str(e)}')
    
    # Import weather alerts
    try:
        results['weather_alerts'] = DisasterDataIntegrator.import_weather_alerts(area)
    except Exception as e:
        results['errors'].append(f'Weather alerts import failed: {str(e)}')
    
    total_imported = results['earthquakes'] + results['weather_alerts']
    
    log_audit_action('IMPORT', 'ALL_DISASTER_DATA', None, 
                    f'Imported {total_imported} total alerts (earthquakes: {results["earthquakes"]}, weather: {results["weather_alerts"]})')
    
    return jsonify({
        'message': f'Import completed - {total_imported} total alerts imported',
        'results': results,
        'total_imported': total_imported
    }), 200


@api_bp.route('/data/sources', methods=['GET'])
@jwt_required()
def get_data_sources():
    """Get information about available external data sources"""
    return jsonify({
        'sources': [
            {
                'name': 'USGS Earthquake API',
                'type': 'earthquakes',
                'description': 'Real-time earthquake data from the United States Geological Survey',
                'url': 'https://earthquake.usgs.gov/fdsnws/event/1/',
                'update_frequency': 'Real-time',
                'coverage': 'Global',
                'min_magnitude': 'Configurable (default: 4.0)'
            },
            {
                'name': 'NOAA Weather Alerts',
                'type': 'weather',
                'description': 'Active weather warnings and alerts from the National Weather Service',
                'url': 'https://api.weather.gov/alerts/active',
                'update_frequency': 'Real-time',
                'coverage': 'United States',
                'alert_types': ['Severe Weather', 'Floods', 'Tornados', 'Hurricanes', 'Blizzards']
            }
        ]
    }), 200