# 📚 CDRP API - Complete User Guide

## 🌐 **Live API Information**

### **Base URL**
```
https://cdrp-api-7cdba03291e5.herokuapp.com
```

### **Admin Credentials**
```
Username: admin
Password: admin123
```

### **API Key (JWT Token)**
After logging in, you'll receive a JWT token that serves as your API key. Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODgwMTEyMCwianRpIjoiMzllYWFkZTItMjI0Ni00YmVlLWIxYTctOGFiZjY5NDg2NDFmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDg4MDExMjAsImNzcmYiOiI5N2FiODMwMi0zZjNlLTQ0NDEtYWNmZC1jODA1OWZiZDYwODMiLCJleHAiOjE3NDg4MDQ3MjB9.Z91uoupWKYKZ7YbK2B-4n-Q_5gMbWdWWgN5PP-Rnd1I
```

---

## 🔐 **Authentication & Permissions System**

### **User Roles Hierarchy**

#### **1. Admin (Highest Privileges)**
- ✅ **Full system access**
- ✅ **Manage all users, regions, disaster types**
- ✅ **View and manage data across ALL regions**
- ✅ **Access audit logs**
- ✅ **Create/delete any resource**

#### **2. Regional Coordinator**
- ✅ **Manage relief requests in their assigned region**
- ✅ **Assign requests to field agents**
- ✅ **Update request status (approve/reject)**
- ✅ **View analytics for their region**
- ❌ **Cannot access other regions**
- ❌ **Cannot manage users or system settings**

#### **3. Field Agent**
- ✅ **Create and update relief requests in their region**
- ✅ **View requests in their region**
- ✅ **Update request details and progress**
- ❌ **Cannot approve/reject requests**
- ❌ **Cannot assign requests to others**
- ❌ **Cannot access other regions**

#### **4. Viewer (Lowest Privileges)**
- ✅ **Read-only access to relief requests in their region**
- ✅ **View regions and disaster types**
- ❌ **Cannot create, update, or delete anything**
- ❌ **Cannot access other regions**

---

## 🚀 **Getting Started - Step by Step**

### **Step 1: Login and Get Your API Token**

```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@cdrp.org",
    "first_name": "System",
    "last_name": "Administrator",
    "role": "admin",
    "region_id": 3,
    "is_active": true,
    "created_at": "2025-06-01T18:04:19.831027",
    "updated_at": "2025-06-01T18:04:19.831032"
  }
}
```

**💡 Save the `access_token` - this is your API key for all subsequent requests!**

### **Step 2: Use Your Token for API Calls**

For all API calls, include your token in the Authorization header:
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 📋 **Complete API Reference with Examples**

### **🔍 Health Check**

```bash
curl https://cdrp-api-7cdba03291e5.herokuapp.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "CDRP API is running"
}
```

---

## 🔐 **Authentication Endpoints**

### **1. User Registration (Admin Only)**

```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/auth/register \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "field_agent_north",
    "email": "agent.north@emergency.gov",
    "password": "SecurePass123!",
    "first_name": "Sarah",
    "last_name": "Johnson",
    "role": "field_agent",
    "region_id": 1
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 4,
    "username": "field_agent_north",
    "email": "agent.north@emergency.gov",
    "first_name": "Sarah",
    "last_name": "Johnson",
    "role": "field_agent",
    "region_id": 1,
    "is_active": true,
    "created_at": "2025-06-01T18:30:00.000000",
    "updated_at": "2025-06-01T18:30:00.000000"
  }
}
```

### **2. Get User Profile**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/auth/profile
```

### **3. Change Password**

```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "admin123",
    "new_password": "NewSecurePassword123!"
  }'
```

### **4. Logout**

```bash
curl -X DELETE https://cdrp-api-7cdba03291e5.herokuapp.com/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🌍 **Reference Data Endpoints**

### **1. Get All Regions**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/regions
```

**Response:**
```json
{
  "regions": [
    {
      "id": 1,
      "name": "North Region",
      "code": "NR",
      "description": "Northern administrative region",
      "coordinates": null,
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    },
    {
      "id": 2,
      "name": "South Region",
      "code": "SR",
      "description": "Southern administrative region",
      "coordinates": null,
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    },
    {
      "id": 3,
      "name": "Central Region",
      "code": "CR",
      "description": "Central administrative region",
      "coordinates": null,
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    }
  ]
}
```

### **2. Get All Disaster Types**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/disaster-types
```

**Response:**
```json
{
  "disaster_types": [
    {
      "id": 1,
      "name": "Earthquake",
      "code": "EQ",
      "description": "Seismic activity",
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    },
    {
      "id": 2,
      "name": "Flood",
      "code": "FL",
      "description": "Water overflow",
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    },
    {
      "id": 3,
      "name": "Hurricane",
      "code": "HU",
      "description": "Tropical cyclone",
      "is_active": true,
      "created_at": "2025-06-01T18:04:19.000000"
    }
  ]
}
```

### **3. Create New Region (Admin Only)**

```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/regions \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "West Region",
    "code": "WR",
    "description": "Western administrative region",
    "coordinates": "34.0522,-118.2437"
  }'
```

---

## 🆘 **Relief Request Management**

### **1. Create a Relief Request (Field Agent+ Required)**

```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Urgent: Flood Relief Needed in Downtown Area",
    "description": "Heavy rainfall has caused severe flooding in the downtown residential district. Multiple families have been displaced and need immediate assistance. Water levels are rising and evacuation may be necessary.",
    "location": "Downtown Residential District, Central City",
    "coordinates": "40.7589,-73.9851",
    "severity": "critical",
    "disaster_type_id": 2,
    "region_id": 3,
    "affected_population": 150,
    "estimated_damage": 500000.00,
    "required_resources": "Emergency shelter, food supplies, clean water, medical aid, evacuation support, pumping equipment",
    "contact_person": "Maria Rodriguez",
    "contact_phone": "+1-555-0199",
    "contact_email": "maria.rodriguez@emergency.gov"
  }'
```

**Response:**
```json
{
  "message": "Relief request created successfully",
  "request": {
    "id": 1,
    "title": "Urgent: Flood Relief Needed in Downtown Area",
    "description": "Heavy rainfall has caused severe flooding...",
    "location": "Downtown Residential District, Central City",
    "coordinates": "40.7589,-73.9851",
    "severity": "critical",
    "status": "pending",
    "disaster_type_id": 2,
    "region_id": 3,
    "created_by": 1,
    "assigned_to": null,
    "affected_population": 150,
    "estimated_damage": 500000.0,
    "required_resources": "Emergency shelter, food supplies...",
    "contact_person": "Maria Rodriguez",
    "contact_phone": "+1-555-0199",
    "contact_email": "maria.rodriguez@emergency.gov",
    "priority_score": null,
    "predicted_by_ml": false,
    "ml_confidence": null,
    "documents": null,
    "created_at": "2025-06-01T18:45:00.000000",
    "updated_at": "2025-06-01T18:45:00.000000",
    "resolved_at": null
  }
}
```

### **2. Get All Relief Requests (With Filtering)**

```bash
# Get all requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests"

# Filter by severity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?severity=critical"

# Filter by status and region
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?status=pending&region_id=3"

# Search with pagination
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?query=flood&page=1&per_page=10"

# Filter by date range
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?date_from=2025-06-01&date_to=2025-06-02"
```

**Response:**
```json
{
  "requests": [
    {
      "id": 1,
      "title": "Urgent: Flood Relief Needed in Downtown Area",
      "description": "Heavy rainfall has caused severe flooding...",
      "location": "Downtown Residential District, Central City",
      "severity": "critical",
      "status": "pending",
      "disaster_type_id": 2,
      "region_id": 3,
      "created_by": 1,
      "assigned_to": null,
      "affected_population": 150,
      "estimated_damage": 500000.0,
      "created_at": "2025-06-01T18:45:00.000000",
      "updated_at": "2025-06-01T18:45:00.000000"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### **3. Get Specific Relief Request**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/1
```

### **4. Update Relief Request**

#### **Field Agent Update (Own Request)**
```bash
curl -X PUT https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/1 \
  -H "Authorization: Bearer YOUR_FIELD_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "affected_population": 175,
    "required_resources": "Emergency shelter, food supplies, clean water, medical aid, evacuation support, pumping equipment, temporary bridges",
    "description": "Heavy rainfall has caused severe flooding in the downtown residential district. Water levels continue to rise. Additional families evacuated. Bridge access compromised."
  }'
```

#### **Coordinator Update (Status & Assignment)**
```bash
curl -X PUT https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/1 \
  -H "Authorization: Bearer YOUR_COORDINATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "assigned_to": 4,
    "priority_score": 9.5
  }'
```

**Response:**
```json
{
  "message": "Relief request updated successfully",
  "request": {
    "id": 1,
    "title": "Urgent: Flood Relief Needed in Downtown Area",
    "status": "approved",
    "assigned_to": 4,
    "affected_population": 175,
    "priority_score": 9.5,
    "updated_at": "2025-06-01T19:00:00.000000"
  }
}
```

### **5. Delete Relief Request (Coordinator+ Only)**

```bash
curl -X DELETE https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/1 \
  -H "Authorization: Bearer YOUR_COORDINATOR_TOKEN"
```

---

## 📊 **Analytics & Reporting**

### **Dashboard Analytics (Coordinator+ Required)**

```bash
curl -H "Authorization: Bearer YOUR_COORDINATOR_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/analytics/dashboard
```

**Response:**
```json
{
  "status_counts": {
    "pending": 5,
    "approved": 3,
    "in_progress": 2,
    "completed": 1,
    "rejected": 0
  },
  "severity_counts": {
    "low": 2,
    "medium": 4,
    "high": 3,
    "critical": 2
  },
  "region_counts": {
    "North Region": 4,
    "South Region": 3,
    "Central Region": 4
  },
  "recent_requests": [
    {
      "id": 1,
      "title": "Urgent: Flood Relief Needed",
      "severity": "critical",
      "status": "approved",
      "created_at": "2025-06-01T18:45:00.000000"
    }
  ],
  "total_requests": 11
}
```

---

## 👥 **User Management (Admin Only)**

### **Get All Users**

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/users
```

### **View Audit Logs**

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/audit-logs?page=1&per_page=50"
```

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "action": "CREATE",
      "resource_type": "RELIEF_REQUEST",
      "resource_id": 1,
      "details": "Created relief request: Urgent: Flood Relief Needed",
      "ip_address": "192.168.1.100",
      "user_agent": "curl/7.68.0",
      "timestamp": "2025-06-01T18:45:00.000000"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 50,
    "total": 15
  }
}
```

---

## 🚫 **Permission Examples & Error Handling**

### **Permission Denied Scenarios**

#### **1. Field Agent Trying to Approve Request**
```bash
curl -X PUT https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/1 \
  -H "Authorization: Bearer FIELD_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

**Response:**
```json
{
  "message": "Permission denied to update status"
}
```

#### **2. Viewer Trying to Create Request**
```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests \
  -H "Authorization: Bearer VIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Emergency", "description": "Help needed"}'
```

**Response:**
```json
{
  "message": "Insufficient permissions"
}
```

#### **3. Regional User Accessing Other Region**
```bash
curl -H "Authorization: Bearer NORTH_REGION_USER_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/south_region_request_id
```

**Response:**
```json
{
  "message": "Access denied to this region"
}
```

### **Validation Error Examples**

#### **Invalid Data**
```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bad",
    "description": "Too short",
    "severity": "invalid_severity",
    "disaster_type_id": 999
  }'
```

**Response:**
```json
{
  "message": "Validation failed",
  "errors": {
    "title": ["Length must be between 5 and 200."],
    "description": ["Length must be at least 10."],
    "location": ["Missing data for required field."],
    "severity": ["Must be one of: low, medium, high, critical."],
    "disaster_type_id": ["Invalid disaster type"],
    "region_id": ["Missing data for required field."]
  }
}
```

---

## 🔄 **Advanced Use Cases**

### **Scenario 1: Emergency Response Workflow**

#### **Step 1: Field Agent Reports Emergency**
```bash
curl -X POST https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests \
  -H "Authorization: Bearer FIELD_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Earthquake Damage - Residential Area",
    "description": "7.2 magnitude earthquake has caused significant structural damage to residential buildings in the Oak Street neighborhood. Multiple buildings collapsed, residents trapped.",
    "location": "Oak Street Neighborhood, Building #45-67",
    "coordinates": "34.0522,-118.2437",
    "severity": "critical",
    "disaster_type_id": 1,
    "region_id": 1,
    "affected_population": 300,
    "estimated_damage": 2500000.00,
    "required_resources": "Search and rescue teams, medical personnel, heavy machinery, temporary shelter, food, water",
    "contact_person": "Captain James Wilson",
    "contact_phone": "+1-555-RESCUE",
    "contact_email": "j.wilson@fire.gov"
  }'
```

#### **Step 2: Coordinator Reviews and Approves**
```bash
curl -X PUT https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/2 \
  -H "Authorization: Bearer COORDINATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "assigned_to": 5,
    "priority_score": 10.0
  }'
```

#### **Step 3: Field Team Updates Progress**
```bash
curl -X PUT https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests/2 \
  -H "Authorization: Bearer ASSIGNED_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "description": "Search and rescue teams deployed. 12 survivors rescued. Heavy machinery on site clearing debris. Medical triage station established."
  }'
```

#### **Step 4: Monitor Progress**
```bash
curl -H "Authorization: Bearer COORDINATOR_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?status=in_progress&severity=critical"
```

### **Scenario 2: Bulk Data Analysis**

#### **Get All Critical Requests by Region**
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "https://cdrp-api-7cdba03291e5.herokuapp.com/api/requests?severity=critical&sort_by=created_at&sort_order=desc"
```

#### **Regional Performance Analytics**
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  https://cdrp-api-7cdba03291e5.herokuapp.com/api/analytics/dashboard
```

---

## 🛠️ **SDK Examples**

### **JavaScript/Node.js**

```javascript
const axios = require('axios');

class CdrpApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
  }
  
  async login(username, password) {
    const response = await axios.post(`${this.baseUrl}/api/auth/login`, {
      username,
      password
    });
    this.token = response.data.access_token;
    return response.data;
  }
  
  async createReliefRequest(requestData) {
    const response = await axios.post(`${this.baseUrl}/api/requests`, requestData, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.data;
  }
  
  async getRequests(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await axios.get(`${this.baseUrl}/api/requests?${params}`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
    return response.data;
  }
}

// Usage
const client = new CdrpApiClient('https://cdrp-api-7cdba03291e5.herokuapp.com');
await client.login('admin', 'admin123');

const newRequest = await client.createReliefRequest({
  title: 'Emergency Relief Needed',
  description: 'Urgent assistance required...',
  location: 'Downtown Area',
  severity: 'high',
  disaster_type_id: 1,
  region_id: 1
});
```

### **Python**

```python
import requests

class CdrpApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/api/auth/login", 
                               json={"username": username, "password": password})
        data = response.json()
        self.token = data['access_token']
        return data
    
    def create_relief_request(self, request_data):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{self.base_url}/api/requests", 
                               json=request_data, headers=headers)
        return response.json()
    
    def get_requests(self, **filters):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/api/requests", 
                              params=filters, headers=headers)
        return response.json()

# Usage
client = CdrpApiClient('https://cdrp-api-7cdba03291e5.herokuapp.com')
client.login('admin', 'admin123')

new_request = client.create_relief_request({
    'title': 'Emergency Relief Needed',
    'description': 'Urgent assistance required...',
    'location': 'Downtown Area',
    'severity': 'high',
    'disaster_type_id': 1,
    'region_id': 1
})
```

---

## 📱 **Mobile App Integration Example**

### **Flutter/Dart**

```dart
class CdrpApiService {
  final String baseUrl = 'https://cdrp-api-7cdba03291e5.herokuapp.com';
  String? token;
  
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'username': username, 'password': password}),
    );
    
    final data = json.decode(response.body);
    token = data['access_token'];
    return data;
  }
  
  Future<List<dynamic>> getReliefRequests({String? severity, String? status}) async {
    final queryParams = <String, String>{};
    if (severity != null) queryParams['severity'] = severity;
    if (status != null) queryParams['status'] = status;
    
    final uri = Uri.parse('$baseUrl/api/requests').replace(queryParameters: queryParams);
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );
    
    final data = json.decode(response.body);
    return data['requests'];
  }
}
```

---

## 🔐 **Security Best Practices**

### **Token Management**
1. **Store tokens securely** (not in localStorage for sensitive apps)
2. **Implement token refresh logic**
3. **Handle expired tokens gracefully**
4. **Use HTTPS only**

### **Rate Limiting**
- **100 requests per hour** per IP address
- **50 requests per minute** for search endpoints
- **10 requests per minute** for creation endpoints

### **Error Handling**
Always check for these HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (invalid/expired token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **409**: Conflict (duplicate data)
- **429**: Too Many Requests (rate limited)
- **500**: Internal Server Error

---

## 🎯 **Quick Reference**

### **Essential Endpoints Summary**
| Method | Endpoint | Purpose | Required Role |
|--------|----------|---------|---------------|
| POST | `/api/auth/login` | Get API token | Any |
| GET | `/api/regions` | List regions | Authenticated |
| GET | `/api/disaster-types` | List disaster types | Authenticated |
| POST | `/api/requests` | Create relief request | Field Agent+ |
| GET | `/api/requests` | List relief requests | Authenticated |
| PUT | `/api/requests/{id}` | Update request | Creator/Coordinator+ |
| GET | `/api/analytics/dashboard` | View analytics | Coordinator+ |
| POST | `/api/auth/register` | Create user | Admin |

### **Severity Levels**
- `low`: Minor incidents, non-urgent
- `medium`: Moderate impact, some urgency
- `high`: Significant impact, urgent response needed
- `critical`: Life-threatening, immediate response required

### **Request Status Flow**
1. `pending` → 2. `approved` → 3. `in_progress` → 4. `completed`
                    ↓
                 `rejected`

**Your CDRP API is now fully documented and ready for integration! 🚀**