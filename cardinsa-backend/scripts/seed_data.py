# scripts/seed_data.py
"""
Sample data seeding script for development
Run with: python scripts/seed_data.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.models.auth.user import User, Role, Permission
from app.models.company.company import Company
from app.models.company.geography import Country, Region, City

def seed_basic_data():
    """Seed basic data for development"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create default company
        company = Company(
            name="Cardinsa Insurance",
            email="admin@cardinsa.com",
            phone="+961-1-123456",
            address="Beirut, Lebanon",
            is_active=True
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create permissions
        permissions = [
            Permission(name="user:create", description="Create users"),
            Permission(name="user:read", description="Read users"),
            Permission(name="user:update", description="Update users"),
            Permission(name="user:delete", description="Delete users"),
            Permission(name="policy:create", description="Create policies"),
            Permission(name="policy:read", description="Read policies"),
            Permission(name="claim:create", description="Create claims"),
            Permission(name="claim:process", description="Process claims"),
        ]
        
        for perm in permissions:
            db.add(perm)
        db.commit()
        
        # Create roles
        admin_role = Role(name="admin", description="System Administrator")
        agent_role = Role(name="agent", description="Insurance Agent")
        member_role = Role(name="member", description="Insurance Member")
        
        # Assign permissions to admin role
        admin_role.permissions = permissions
        
        db.add(admin_role)
        db.add(agent_role)
        db.add(member_role)
        db.commit()
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@cardinsa.com",
            first_name="System",
            last_name="Administrator",
            company_id=company.id,
            is_active=True
        )
        admin_user.set_password("admin123!")
        admin_user.roles = [admin_role]
        
        db.add(admin_user)
        db.commit()
        
        # Create sample countries
        lebanon = Country(name="Lebanon", iso_code="LB", phone_code="+961")
        uae = Country(name="United Arab Emirates", iso_code="AE", phone_code="+971")
        
        db.add(lebanon)
        db.add(uae)
        db.commit()
        
        # Create sample regions
        beirut_region = Region(name="Beirut", code="BEI", country_id=lebanon.id)
        dubai_region = Region(name="Dubai", code="DXB", country_id=uae.id)
        
        db.add(beirut_region)
        db.add(dubai_region)
        db.commit()
        
        print("Sample data seeded successfully!")
        print(f"Admin user created: username=admin, password=admin123!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_basic_data()