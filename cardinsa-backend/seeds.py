#!/usr/bin/env python3
"""
Database seeder for Cardinsa Insurance API.
Creates initial admin user, roles, permissions, and organizational structure.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.config.database import db_manager
from app.core.security import hash_password
from app.models.auth.user import (
    User, Role, Permission, Department, Unit, 
    UserPassword, user_roles, role_permissions
)


async def create_permissions(db_session):
    """Create initial permissions."""
    permissions_data = [
        # User management permissions
        ("users.read", "Read Users", "users", "read", "all", "View user information"),
        ("users.create", "Create Users", "users", "create", "all", "Create new users"),
        ("users.update", "Update Users", "users", "update", "all", "Update user information"),
        ("users.delete", "Delete Users", "users", "delete", "all", "Delete users"),
        ("users.read.own", "Read Own Profile", "users", "read", "own", "View own user information"),
        ("users.update.own", "Update Own Profile", "users", "update", "own", "Update own user information"),
        
        # Role management permissions
        ("roles.read", "Read Roles", "roles", "read", "all", "View role information"),
        ("roles.create", "Create Roles", "roles", "create", "all", "Create new roles"),
        ("roles.update", "Update Roles", "roles", "update", "all", "Update role information"),
        ("roles.delete", "Delete Roles", "roles", "delete", "all", "Delete roles"),
        
        # Permission management permissions
        ("permissions.read", "Read Permissions", "permissions", "read", "all", "View permission information"),
        ("permissions.create", "Create Permissions", "permissions", "create", "all", "Create new permissions"),
        ("permissions.update", "Update Permissions", "permissions", "update", "all", "Update permissions"),
        ("permissions.delete", "Delete Permissions", "permissions", "delete", "all", "Delete permissions"),
        
        # Department management permissions
        ("departments.read", "Read Departments", "departments", "read", "all", "View department information"),
        ("departments.create", "Create Departments", "departments", "create", "all", "Create new departments"),
        ("departments.update", "Update Departments", "departments", "update", "all", "Update departments"),
        ("departments.delete", "Delete Departments", "departments", "delete", "all", "Delete departments"),
        ("departments.manage", "Manage Department", "departments", "manage", "own", "Manage own department"),
        
        # Unit management permissions
        ("units.read", "Read Units", "units", "read", "all", "View unit information"),
        ("units.create", "Create Units", "units", "create", "all", "Create new units"),
        ("units.update", "Update Units", "units", "update", "all", "Update unit information"),
        ("units.delete", "Delete Units", "units", "delete", "all", "Delete units"),
        ("units.manage", "Manage Unit", "units", "manage", "own", "Manage own unit"),
        
        # System administration permissions
        ("system.admin", "System Administration", "system", "admin", "all", "Full system administration"),
        ("system.audit", "System Audit", "system", "audit", "all", "View audit logs and system info"),
        ("system.backup", "System Backup", "system", "backup", "all", "Perform system backups"),
        
        # Authentication permissions
        ("auth.manage_sessions", "Manage Sessions", "auth", "manage", "all", "Manage user sessions"),
        ("auth.view_logs", "View Auth Logs", "auth", "view", "all", "View authentication logs"),
    ]
    
    permissions = []
    for code, name, resource, action, scope, description in permissions_data:
        permission = Permission(
            code=code,
            name=name,
            resource=resource,
            action=action,
            scope=scope,
            description=description,
            is_system_permission=True
        )
        db_session.add(permission)
        permissions.append(permission)
        print(f"✅ Created permission: {code}")
    
    await db_session.flush()
    return permissions


async def create_roles(db_session, permissions):
    """Create initial roles."""
    # Create permission lookup
    permission_map = {p.code: p for p in permissions}
    
    roles_data = [
        (
            "superadmin", 
            "Super Administrator", 
            "Full system access with all permissions", 
            100,
            [p.code for p in permissions]  # All permissions
        ),
        (
            "admin",
            "Administrator", 
            "System administration with most permissions",
            90,
            [
                "users.read", "users.create", "users.update", "users.delete",
                "roles.read", "roles.create", "roles.update", 
                "departments.read", "departments.create", "departments.update",
                "units.read", "units.create", "units.update",
                "system.audit", "auth.manage_sessions", "auth.view_logs"
            ]
        ),
        (
            "hr_manager",
            "HR Manager",
            "Human resources management permissions",
            70,
            [
                "users.read", "users.create", "users.update",
                "roles.read", "departments.read", "units.read",
                "departments.manage", "units.manage"
            ]
        ),
        (
            "department_manager",
            "Department Manager",
            "Department-level management permissions",
            50,
            [
                "users.read", "departments.read", "departments.manage",
                "units.read", "units.manage"
            ]
        ),
        (
            "employee",
            "Employee",
            "Basic employee permissions",
            10,
            [
                "users.read.own", "users.update.own",
                "departments.read", "units.read"
            ]
        )
    ]
    
    roles = []
    for code, name, description, level, permission_codes in roles_data:
        role = Role(
            code=code,
            name=name,
            description=description,
            level=level,
            is_system_role=True,
            is_active=True
        )
        db_session.add(role)
        roles.append((role, permission_codes))
        print(f"✅ Created role: {code}")
    
    await db_session.flush()
    
    # Assign permissions to roles
    for role, permission_codes in roles:
        for perm_code in permission_codes:
            if perm_code in permission_map:
                db_session.execute(
                    role_permissions.insert().values(
                        role_id=role.id,
                        permission_id=permission_map[perm_code].id
                    )
                )
        print(f"✅ Assigned {len(permission_codes)} permissions to role: {role.code}")
    
    return [role for role, _ in roles]


async def create_departments_and_units(db_session):
    """Create initial organizational structure."""
    # Create departments
    departments_data = [
        ("IT", "Information Technology", "Technology and systems management"),
        ("HR", "Human Resources", "Human resources and employee management"),
        ("FIN", "Finance", "Financial operations and accounting"),
        ("OPS", "Operations", "Business operations and processes"),
        ("SALES", "Sales", "Sales and business development"),
    ]
    
    departments = []
    for code, name, description in departments_data:
        department = Department(
            code=code,
            name=name,
            description=description,
            is_active=True
        )
        db_session.add(department)
        departments.append(department)
        print(f"✅ Created department: {code}")
    
    await db_session.flush()
    
    # Create units
    units_data = [
        ("IT-DEV", "Development", "Software development team", "IT"),
        ("IT-OPS", "IT Operations", "IT operations and infrastructure", "IT"),
        ("HR-REC", "Recruitment", "Talent acquisition and recruitment", "HR"),
        ("HR-PAY", "Payroll", "Payroll and benefits administration", "HR"),
        ("FIN-ACC", "Accounting", "Financial accounting and reporting", "FIN"),
        ("OPS-PROC", "Process Management", "Business process management", "OPS"),
    ]
    
    dept_map = {d.code: d for d in departments}
    units = []
    
    for code, name, description, dept_code in units_data:
        unit = Unit(
            code=code,
            name=name,
            description=description,
            department_id=dept_map[dept_code].id,
            is_active=True
        )
        db_session.add(unit)
        units.append(unit)
        print(f"✅ Created unit: {code} in department {dept_code}")
    
    await db_session.flush()
    return departments, units


async def create_admin_user(db_session, roles, departments):
    """Create initial admin user."""
    # Find the superadmin role and IT department
    superadmin_role = next((r for r in roles if r.code == "superadmin"), None)
    it_department = next((d for d in departments if d.code == "IT"), None)
    
    if not superadmin_role:
        print("❌ Could not find superadmin role")
        return None
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@cardinsa.com",
        first_name="System",
        last_name="Administrator",
        is_active=True,
        is_staff=True,
        is_superuser=True,
        email_verified=True,
        department_id=it_department.id if it_department else None,
        timezone="UTC",
        language="en"
    )
    db_session.add(admin_user)
    await db_session.flush()
    
    # Create admin password
    admin_password = UserPassword(
        user_id=admin_user.id,
        password_hash=hash_password("Admin123!"),
        is_current=True
    )
    db_session.add(admin_password)
    
    # Assign superadmin role
    db_session.execute(
        user_roles.insert().values(
            user_id=admin_user.id,
            role_id=superadmin_role.id,
            assigned_at=datetime.utcnow(),
            is_active=True
        )
    )
    
    print(f"✅ Created admin user: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Password: Admin123!")
    print(f"   Role: {superadmin_role.name}")
    
    return admin_user


async def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    
    try:
        # Initialize database manager
        db_manager.initialize()
        
        # Check database connection
        if not await db_manager.check_connection():
            print("❌ Database connection failed")
            return False
        
        print("✅ Database connection verified")
        
        # Get database session
        async with db_manager.get_db_context() as db_session:
            print("📊 Creating initial data...")
            
            # Create permissions
            permissions = await create_permissions(db_session)
            print(f"✅ Created {len(permissions)} permissions")
            
            # Create roles
            roles = await create_roles(db_session, permissions)
            print(f"✅ Created {len(roles)} roles")
            
            # Create departments and units
            departments, units = await create_departments_and_units(db_session)
            print(f"✅ Created {len(departments)} departments and {len(units)} units")
            
            # Create admin user
            admin_user = await create_admin_user(db_session, roles, departments)
            
            # Commit all changes
            await db_session.commit()
            print("✅ All changes committed to database")
            
            print("\n🎉 Database seeding completed successfully!")
            print("\n📋 Summary:")
            print(f"   • Permissions: {len(permissions)}")
            print(f"   • Roles: {len(roles)}")
            print(f"   • Departments: {len(departments)}")
            print(f"   • Units: {len(units)}")
            print(f"   • Admin User: {admin_user.username if admin_user else 'Failed'}")
            
            print("\n🔑 Admin Login Credentials:")
            print("   • Username: admin")
            print("   • Email: admin@cardinsa.com")
            print("   • Password: Admin123!")
            
            print("\n🚀 You can now start the API and login with these credentials!")
            
            return True
            
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_existing_data(db_session):
    """Check if data already exists."""
    try:
        # Check if admin user exists
        result = await db_session.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        user_count = result.scalar()
        
        # Check if roles exist
        result = await db_session.execute("SELECT COUNT(*) FROM roles WHERE is_system_role = true")
        role_count = result.scalar()
        
        # Check if permissions exist
        result = await db_session.execute("SELECT COUNT(*) FROM permissions WHERE is_system_permission = true")
        permission_count = result.scalar()
        
        return user_count > 0 or role_count > 0 or permission_count > 0
        
    except Exception as e:
        print(f"Warning: Could not check existing data: {e}")
        return False


async def reset_and_seed():
    """Reset database and seed fresh data."""
    print("⚠️ This will delete all existing data and recreate it!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return False
    
    try:
        # Initialize database manager
        db_manager.initialize()
        
        # Drop and recreate tables
        print("🗑️ Dropping existing tables...")
        await db_manager.drop_all_tables()
        
        print("🏗️ Creating fresh tables...")
        await db_manager.create_all_tables()
        
        # Seed the database
        return await seed_database()
        
    except Exception as e:
        print(f"❌ Reset and seed failed: {e}")
        return False


def main():
    """Main function with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database seeder for Cardinsa Insurance API")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Drop all tables and recreate with fresh data"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force seeding even if data exists"
    )
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            success = asyncio.run(reset_and_seed())
        else:
            success = asyncio.run(seed_database())
        
        if success:
            print("\n✅ Database seeding completed successfully!")
            print("\n🔗 Next steps:")
            print("   1. Start the API: python main.py")
            print("   2. Visit: http://localhost:8001/docs")
            print("   3. Login with admin credentials")
            sys.exit(0)
        else:
            print("\n❌ Database seeding failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()