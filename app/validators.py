from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from email_validator import validate_email, EmailNotValidError
from app.models import UserRole, DisasterSeverity, RequestStatus


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    role = fields.Str(validate=validate.OneOf([role.value for role in UserRole]), missing=UserRole.VIEWER.value)
    region_id = fields.Int(allow_none=True)


class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserUpdateSchema(Schema):
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    role = fields.Str(validate=validate.OneOf([role.value for role in UserRole]))
    region_id = fields.Int(allow_none=True)
    is_active = fields.Bool()


class PasswordResetSchema(Schema):
    email = fields.Email(required=True)


class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))


class ReliefRequestSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    location = fields.Str(required=True, validate=validate.Length(min=5, max=255))
    coordinates = fields.Str(validate=validate.Length(max=255))
    severity = fields.Str(required=True, validate=validate.OneOf([severity.value for severity in DisasterSeverity]))
    disaster_type_id = fields.Int(required=True)
    region_id = fields.Int(required=True)
    affected_population = fields.Int(validate=validate.Range(min=0))
    estimated_damage = fields.Float(validate=validate.Range(min=0))
    required_resources = fields.Str()
    contact_person = fields.Str(validate=validate.Length(max=100))
    contact_phone = fields.Str(validate=validate.Length(max=20))
    contact_email = fields.Email()


class ReliefRequestUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=5, max=200))
    description = fields.Str(validate=validate.Length(min=10))
    location = fields.Str(validate=validate.Length(min=5, max=255))
    coordinates = fields.Str(validate=validate.Length(max=255))
    severity = fields.Str(validate=validate.OneOf([severity.value for severity in DisasterSeverity]))
    status = fields.Str(validate=validate.OneOf([status.value for status in RequestStatus]))
    disaster_type_id = fields.Int()
    region_id = fields.Int()
    assigned_to = fields.Int(allow_none=True)
    affected_population = fields.Int(validate=validate.Range(min=0))
    estimated_damage = fields.Float(validate=validate.Range(min=0))
    required_resources = fields.Str()
    contact_person = fields.Str(validate=validate.Length(max=100))
    contact_phone = fields.Str(validate=validate.Length(max=20))
    contact_email = fields.Email()


class RegionSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=2, max=10))
    description = fields.Str()
    coordinates = fields.Str(validate=validate.Length(max=255))
    is_active = fields.Bool()


class DisasterTypeSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    code = fields.Str(required=True, validate=validate.Length(min=2, max=10))
    description = fields.Str()
    is_active = fields.Bool()


class SearchSchema(Schema):
    query = fields.Str()
    region_id = fields.Int()
    disaster_type_id = fields.Int()
    severity = fields.Str(validate=validate.OneOf([severity.value for severity in DisasterSeverity]))
    status = fields.Str(validate=validate.OneOf([status.value for status in RequestStatus]))
    created_by = fields.Int()
    assigned_to = fields.Int()
    date_from = fields.Date()
    date_to = fields.Date()
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)
    sort_by = fields.Str(validate=validate.OneOf(['created_at', 'updated_at', 'severity', 'status']), missing='created_at')
    sort_order = fields.Str(validate=validate.OneOf(['asc', 'desc']), missing='desc')

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise ValidationError('date_from must be before date_to')


def validate_request_data(schema_class, data):
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages


def validate_email_format(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False