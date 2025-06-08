import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Region, DisasterType, UserRole
from datetime import datetime, timezone

def seed_data():
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        print("Seeding database with initial data...")
        
        # Create regions
        regions_data = [
            {"name": "North Region", "code": "NR", "description": "Northern administrative region"},
            {"name": "South Region", "code": "SR", "description": "Southern administrative region"},
            {"name": "East Region", "code": "ER", "description": "Eastern administrative region"},
            {"name": "West Region", "code": "WR", "description": "Western administrative region"},
            {"name": "Central Region", "code": "CR", "description": "Central administrative region"},
        ]
        
        for region_data in regions_data:
            existing_region = Region.query.filter_by(code=region_data["code"]).first()
            if not existing_region:
                region = Region(**region_data)
                db.session.add(region)
                print(f"Created region: {region_data['name']}")
        
        # Create disaster types
        disaster_types_data = [
            {"name": "Earthquake", "code": "EQ", "description": "Seismic activity causing ground shaking"},
            {"name": "Flood", "code": "FL", "description": "Overflow of water onto normally dry land"},
            {"name": "Hurricane", "code": "HU", "description": "Tropical cyclone with sustained winds"},
            {"name": "Wildfire", "code": "WF", "description": "Uncontrolled fire in vegetation areas"},
            {"name": "Tornado", "code": "TO", "description": "Violently rotating column of air"},
            {"name": "Drought", "code": "DR", "description": "Prolonged period of abnormally low rainfall"},
            {"name": "Tsunami", "code": "TS", "description": "Series of ocean waves caused by displacement"},
            {"name": "Volcanic Eruption", "code": "VE", "description": "Explosive discharge from a volcano"},
            {"name": "Landslide", "code": "LS", "description": "Movement of rock, earth, or debris down a slope"},
            {"name": "Blizzard", "code": "BZ", "description": "Severe snowstorm with strong winds"},
        ]
        
        for disaster_data in disaster_types_data:
            existing_disaster = DisasterType.query.filter_by(code=disaster_data["code"]).first()
            if not existing_disaster:
                disaster_type = DisasterType(**disaster_data)
                db.session.add(disaster_type)
                print(f"Created disaster type: {disaster_data['name']}")
        
        # Commit regions and disaster types first
        db.session.commit()
        
        # Create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            central_region = Region.query.filter_by(code='CR').first()
            admin_user = User(
                username='admin',
                email='admin@cdrp.org',
                first_name='System',
                last_name='Administrator',
                role=UserRole.ADMIN,
                region_id=central_region.id if central_region else None
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            print("Created admin user (username: admin, password: admin123)")
        
        # Create regional coordinators
        coordinators_data = [
            {"username": "coord_north", "email": "north@cdrp.org", "first_name": "North", "last_name": "Coordinator", "region_code": "NR"},
            {"username": "coord_south", "email": "south@cdrp.org", "first_name": "South", "last_name": "Coordinator", "region_code": "SR"},
            {"username": "coord_east", "email": "east@cdrp.org", "first_name": "East", "last_name": "Coordinator", "region_code": "ER"},
            {"username": "coord_west", "email": "west@cdrp.org", "first_name": "West", "last_name": "Coordinator", "region_code": "WR"},
        ]
        
        for coord_data in coordinators_data:
            existing_coord = User.query.filter_by(username=coord_data["username"]).first()
            if not existing_coord:
                region = Region.query.filter_by(code=coord_data["region_code"]).first()
                coordinator = User(
                    username=coord_data["username"],
                    email=coord_data["email"],
                    first_name=coord_data["first_name"],
                    last_name=coord_data["last_name"],
                    role=UserRole.REGIONAL_COORDINATOR,
                    region_id=region.id if region else None
                )
                coordinator.set_password('coordinator123')  # Change this in production!
                db.session.add(coordinator)
                print(f"Created coordinator: {coord_data['username']}")
        
        # Create field agents
        agents_data = [
            {"username": "agent_north1", "email": "agent1.north@cdrp.org", "first_name": "Agent", "last_name": "North One", "region_code": "NR"},
            {"username": "agent_north2", "email": "agent2.north@cdrp.org", "first_name": "Agent", "last_name": "North Two", "region_code": "NR"},
            {"username": "agent_south1", "email": "agent1.south@cdrp.org", "first_name": "Agent", "last_name": "South One", "region_code": "SR"},
            {"username": "agent_east1", "email": "agent1.east@cdrp.org", "first_name": "Agent", "last_name": "East One", "region_code": "ER"},
        ]
        
        for agent_data in agents_data:
            existing_agent = User.query.filter_by(username=agent_data["username"]).first()
            if not existing_agent:
                region = Region.query.filter_by(code=agent_data["region_code"]).first()
                agent = User(
                    username=agent_data["username"],
                    email=agent_data["email"],
                    first_name=agent_data["first_name"],
                    last_name=agent_data["last_name"],
                    role=UserRole.FIELD_AGENT,
                    region_id=region.id if region else None
                )
                agent.set_password('agent123')  # Change this in production!
                db.session.add(agent)
                print(f"Created field agent: {agent_data['username']}")
        
        # Create viewer users
        viewers_data = [
            {"username": "viewer1", "email": "viewer1@cdrp.org", "first_name": "John", "last_name": "Viewer", "region_code": "NR"},
            {"username": "viewer2", "email": "viewer2@cdrp.org", "first_name": "Jane", "last_name": "Observer", "region_code": "SR"},
        ]
        
        for viewer_data in viewers_data:
            existing_viewer = User.query.filter_by(username=viewer_data["username"]).first()
            if not existing_viewer:
                region = Region.query.filter_by(code=viewer_data["region_code"]).first()
                viewer = User(
                    username=viewer_data["username"],
                    email=viewer_data["email"],
                    first_name=viewer_data["first_name"],
                    last_name=viewer_data["last_name"],
                    role=UserRole.VIEWER,
                    region_id=region.id if region else None
                )
                viewer.set_password('viewer123')  # Change this in production!
                db.session.add(viewer)
                print(f"Created viewer: {viewer_data['username']}")
        
        # Commit all users
        db.session.commit()
        
        print("\nDatabase seeding completed!")
        print("\nDefault login credentials:")
        print("Admin: admin / admin123")
        print("Coordinators: coord_[region] / coordinator123")
        print("Field Agents: agent_[region][number] / agent123") 
        print("Viewers: viewer[number] / viewer123")
        print("\nREMEMBER TO CHANGE THESE PASSWORDS IN PRODUCTION!")

if __name__ == '__main__':
    seed_data()