import pytest
import json


class TestAuth:
    
    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_login_success(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'testadmin',
            'password': 'testpass'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'testadmin'
    
    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'testadmin',
            'password': 'wrongpass'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['message'] == 'Invalid credentials'
    
    def test_login_missing_fields(self, client):
        response = client.post('/api/auth/login', json={
            'username': 'testadmin'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_get_profile(self, client, admin_token):
        response = client.get('/api/auth/profile', 
                            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == 'testadmin'
    
    def test_get_profile_no_token(self, client):
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
    
    def test_register_new_user(self, client):
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'viewer'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['username'] == 'newuser'
    
    def test_register_duplicate_username(self, client):
        response = client.post('/api/auth/register', json={
            'username': 'testadmin',
            'email': 'another@test.com',
            'password': 'newpass123',
            'first_name': 'Another',
            'last_name': 'User'
        })
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['message']