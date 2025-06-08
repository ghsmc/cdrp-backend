# Disaster Relief API (CDRP API)

A comprehensive REST API for managing disaster relief requests and coordinati2ng emergency response efforts. Built with Flask, this API provides role-based access control, real-time tracking of relief operations, and integration capabilities for predictive disaster management systems.

## Features

### Core Functionality
- **Relief Request Management**: Create, update, track, and manage disaster relief requests
- **User Management**: Role-based access control with Admin, Regional Coordinator, Field Agent, and Viewer roles
- **Regional Organization**: Organize relief efforts by geographical regions
- **Disaster Type Classification**: Support for various disaster types (earthquakes, floods, hurricanes, etc.)
- **Real-time Status Tracking**: Track request status from pending to completion
- **Analytics Dashboard**: Comprehensive analytics for decision-making

### Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Permissions**: Fine-grained access control based on user roles
- **Region-Based Access**: Users can only access data from their assigned regions (except admins)
- **Audit Logging**: Complete audit trail of all actions
- **Rate Limiting**: API rate limiting to prevent abuse

### Technical Features
- **RESTful API Design**: Clean, intuitive API endpoints
- **Input Validation**: Comprehensive request validation using Marshmallow
- **Database Migrations**: Managed database schema updates with Flask-Migrate
- **Pagination**: Efficient data retrieval with pagination support
- **Search & Filtering**: Advanced search and filtering capabilities
- **CORS Support**: Cross-origin resource sharing for web applications

## Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- SQLite (for development) or PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "CDRP API"
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   export FLASK_APP=app.py
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Seed initial data**
   ```bash
   python scripts/seed_data.py
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5001`

## Default Credentials

After running the seed script, you can use these default credentials:

- **Admin**: `admin` / `admin123`
- **Regional Coordinators**: `coord_[region]` / `coordinator123`
- **Field Agents**: `agent_[region][number]` / `agent123`
- **Viewers**: `viewer[number]` / `viewer123`

**⚠️ IMPORTANT: Change these passwords in production!**

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/refresh` | Refresh access token |
| DELETE | `/api/auth/logout` | User logout |
| GET | `/api/auth/profile` | Get user profile |
| PUT | `/api/auth/profile` | Update user profile |
| POST | `/api/auth/change-password` | Change password |

### Relief Request Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/api/requests` | List relief requests | All authenticated users |
| POST | `/api/requests` | Create relief request | Field Agent+ |
| GET | `/api/requests/{id}` | Get specific request | All authenticated users |
| PUT | `/api/requests/{id}` | Update relief request | Field Agent+ |
| DELETE | `/api/requests/{id}` | Delete relief request | Coordinator+ |

### Reference Data Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/api/regions` | List regions | All authenticated users |
| POST | `/api/regions` | Create region | Admin only |
| GET | `/api/disaster-types` | List disaster types | All authenticated users |
| POST | `/api/disaster-types` | Create disaster type | Admin only |

### Analytics Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard analytics | Coordinator+ |

### Admin Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| GET | `/api/users` | List all users | Admin only |
| GET | `/api/audit-logs` | View audit logs | Admin only |

## User Roles & Permissions

### Admin
- Full system access
- Manage users, regions, and disaster types
- View all data across regions
- Access audit logs

### Regional Coordinator
- Manage relief requests in their region
- Assign requests to field agents
- Update request status
- View analytics for their region

### Field Agent
- Create and update relief requests
- View requests in their region
- Cannot assign requests or change status to approved/rejected

### Viewer
- Read-only access to relief requests in their region
- Cannot create or modify data

## Request/Response Examples

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@cdrp.org",
    "role": "admin",
    "region_id": 5
  }
}
```

### Create Relief Request
```bash
POST /api/requests
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Emergency Relief Required for Earthquake",
  "description": "Major earthquake has caused significant damage...",
  "location": "Downtown Central District",
  "coordinates": "40.7128,-74.0060",
  "severity": "high",
  "disaster_type_id": 1,
  "region_id": 5,
  "affected_population": 500,
  "estimated_damage": 1500000.00,
  "required_resources": "Food, water, temporary shelter, medical supplies",
  "contact_person": "John Emergency",
  "contact_phone": "+1-555-0123",
  "contact_email": "john.emergency@example.com"
}
```

### Search Relief Requests
```bash
GET /api/requests?severity=high&status=pending&page=1&per_page=20
Authorization: Bearer <access_token>
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/testing/production) | development |
| `DATABASE_URL` | Database connection string | sqlite:///dev.db |
| `JWT_SECRET_KEY` | JWT signing key | (required in production) |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token expiry (seconds) | 3600 |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token expiry (seconds) | 2592000 |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |
| `REDIS_URL` | Redis connection for rate limiting | redis://localhost:6379/0 |

### Database Configuration

For production, use PostgreSQL:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/cdrp_api_prod
```

## Development

### Project Structure
```
CDRP API/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication endpoints
│   ├── routes.py            # Main API endpoints
│   ├── permissions.py       # Role-based access control
│   └── validators.py        # Input validation schemas
├── config/
│   ├── __init__.py
│   └── config.py            # Configuration classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_auth.py         # Authentication tests
│   └── test_relief_requests.py  # API endpoint tests
├── scripts/
│   ├── __init__.py
│   └── seed_data.py         # Database seeding script
├── migrations/              # Database migrations
├── docs/                    # Documentation
├── app.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage
python -m pytest tests/ --cov=app
```

### Code Quality
```bash
# Format code
black app/ tests/ scripts/

# Lint code
flake8 app/ tests/ scripts/

# Type checking (if mypy is installed)
mypy app/
```

## Deployment

### Production Checklist

1. **Environment Variables**
   - Set strong `JWT_SECRET_KEY`
   - Configure production `DATABASE_URL`
   - Set appropriate `CORS_ORIGINS`
   - Configure Redis for rate limiting

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Run migrations: `flask db upgrade`
   - Seed initial data: `python scripts/seed_data.py`

3. **Security**
   - Change all default passwords
   - Enable HTTPS
   - Set up proper firewall rules
   - Configure rate limiting with Redis

4. **WSGI Server**
   ```bash
   # Using Gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

5. **Reverse Proxy**
   Configure Nginx or Apache as reverse proxy

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the API tests for usage examples

---

**Note**: This is a demo implementation. For production use, additional security measures, monitoring, and performance optimizations should be implemented.