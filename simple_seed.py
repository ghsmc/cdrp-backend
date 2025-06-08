#!/usr/bin/env python3
"""
Simple seed script that works with the initialized database
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def simple_seed():
    """Seed database with basic data using direct SQL"""
    from app import create_app, db
    from app.models import User, Region, DisasterType, UserRole
    
    config_name = os.environ.get('FLASK_ENV', 'production')
    app = create_app(config_name)
    
    with app.app_context():
        print("Seeding database with initial data...")
        
        # Check if data already exists
        if User.query.first():
            print("Database already seeded!")
            return
        
        try:
            # Create regions
            regions_data = [
                {"name": "North Region", "code": "NR", "description": "Northern administrative region"},
                {"name": "South Region", "code": "SR", "description": "Southern administrative region"},
                {"name": "Central Region", "code": "CR", "description": "Central administrative region"},
            ]
            
            for region_data in regions_data:
                region = Region(**region_data)
                db.session.add(region)
            
            # Create disaster types
            disaster_types_data = [
                {"name": "Earthquake", "code": "EQ", "description": "Seismic activity"},
                {"name": "Flood", "code": "FL", "description": "Water overflow"},
                {"name": "Hurricane", "code": "HU", "description": "Tropical cyclone"},
            ]
            
            for disaster_data in disaster_types_data:
                disaster_type = DisasterType(**disaster_data)
                db.session.add(disaster_type)
            
            db.session.commit()
            print("Created regions and disaster types")
            
            # Create admin user
            central_region = Region.query.filter_by(code='CR').first()
            admin_user = User(
                username='admin',
                email='admin@cdrp.org',
                first_name='System',
                last_name='Administrator',
                role=UserRole.ADMIN,
                region_id=central_region.id if central_region else None
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            db.session.commit()
            print("Created admin user")
            print("Database seeding completed successfully!")
            print("Login with: admin / admin123")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during seeding: {e}")
            raise

if __name__ == '__main__':
    simple_seed()