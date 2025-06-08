import pytest
import os
import tempfile
from app import create_app, db
from app.models import User, Region, DisasterType, UserRole


@pytest.fixture
def client():
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['DATABASE_URL'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create test data
            region = Region(name='Test Region', code='TEST', description='Test region')
            db.session.add(region)
            db.session.commit()
            
            disaster_type = DisasterType(name='Test Disaster', code='TEST', description='Test disaster')
            db.session.add(disaster_type)
            db.session.commit()
            
            # Create test users
            admin_user = User(
                username='testadmin',
                email='admin@test.com',
                first_name='Test',
                last_name='Admin',
                role=UserRole.ADMIN,
                region_id=region.id
            )
            admin_user.set_password('testpass')
            db.session.add(admin_user)
            
            field_agent = User(
                username='testagent',
                email='agent@test.com',
                first_name='Test',
                last_name='Agent',
                role=UserRole.FIELD_AGENT,
                region_id=region.id
            )
            field_agent.set_password('testpass')
            db.session.add(field_agent)
            
            db.session.commit()
            
        yield client
        
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def admin_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testadmin',
        'password': 'testpass'
    })
    return response.json['access_token']


@pytest.fixture
def agent_token(client):
    response = client.post('/api/auth/login', json={
        'username': 'testagent',
        'password': 'testpass'
    })
    return response.json['access_token']