import pytest
import json


class TestReliefRequests:
    
    def test_get_regions(self, client, admin_token):
        response = client.get('/api/regions',
                            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'regions' in data
        assert len(data['regions']) > 0
    
    def test_get_disaster_types(self, client, admin_token):
        response = client.get('/api/disaster-types',
                            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'disaster_types' in data
        assert len(data['disaster_types']) > 0
    
    def test_create_relief_request(self, client, agent_token):
        response = client.post('/api/requests', 
                             headers={'Authorization': f'Bearer {agent_token}'},
                             json={
                                 'title': 'Test Emergency',
                                 'description': 'This is a test emergency requiring immediate attention',
                                 'location': 'Test Location',
                                 'severity': 'high',
                                 'disaster_type_id': 1,
                                 'region_id': 1,
                                 'affected_population': 100,
                                 'contact_person': 'Test Contact',
                                 'contact_phone': '+1-555-0199'
                             })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['request']['title'] == 'Test Emergency'
        assert data['request']['status'] == 'pending'
    
    def test_get_relief_requests(self, client, admin_token):
        # First create a request
        client.post('/api/requests', 
                   headers={'Authorization': f'Bearer {admin_token}'},
                   json={
                       'title': 'Test Emergency for List',
                       'description': 'This is a test emergency for listing',
                       'location': 'Test Location',
                       'severity': 'medium',
                       'disaster_type_id': 1,
                       'region_id': 1,
                       'affected_population': 50
                   })
        
        # Then get all requests
        response = client.get('/api/requests',
                            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'requests' in data
        assert 'pagination' in data
        assert len(data['requests']) > 0
    
    def test_get_relief_request_by_id(self, client, admin_token):
        # First create a request
        create_response = client.post('/api/requests', 
                                    headers={'Authorization': f'Bearer {admin_token}'},
                                    json={
                                        'title': 'Test Emergency for Get',
                                        'description': 'This is a test emergency for getting by ID',
                                        'location': 'Test Location',
                                        'severity': 'low',
                                        'disaster_type_id': 1,
                                        'region_id': 1,
                                        'affected_population': 25
                                    })
        request_id = json.loads(create_response.data)['request']['id']
        
        # Then get the specific request
        response = client.get(f'/api/requests/{request_id}',
                            headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['request']['id'] == request_id
        assert data['request']['title'] == 'Test Emergency for Get'
    
    def test_update_relief_request(self, client, admin_token):
        # First create a request
        create_response = client.post('/api/requests', 
                                    headers={'Authorization': f'Bearer {admin_token}'},
                                    json={
                                        'title': 'Test Emergency for Update',
                                        'description': 'This is a test emergency for updating',
                                        'location': 'Test Location',
                                        'severity': 'low',
                                        'disaster_type_id': 1,
                                        'region_id': 1,
                                        'affected_population': 25
                                    })
        request_id = json.loads(create_response.data)['request']['id']
        
        # Then update the request
        response = client.put(f'/api/requests/{request_id}',
                            headers={'Authorization': f'Bearer {admin_token}'},
                            json={
                                'title': 'Updated Emergency Title',
                                'status': 'approved',
                                'affected_population': 75
                            })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['request']['title'] == 'Updated Emergency Title'
        assert data['request']['status'] == 'approved'
        assert data['request']['affected_population'] == 75
    
    def test_create_relief_request_validation_error(self, client, agent_token):
        response = client.post('/api/requests', 
                             headers={'Authorization': f'Bearer {agent_token}'},
                             json={
                                 'title': 'Short',  # Too short
                                 'description': 'Too short',  # Too short
                                 'location': 'Test Location',
                                 'severity': 'invalid',  # Invalid severity
                                 'disaster_type_id': 999,  # Invalid disaster type
                                 'region_id': 999  # Invalid region
                             })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
    
    def test_unauthorized_access(self, client):
        response = client.get('/api/requests')
        assert response.status_code == 401