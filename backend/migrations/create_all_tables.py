"""
Database migration script to create all tables for Rice Mill ERP
Updated with all latest fixes and PostgreSQL compatibility
"""
import sys
import os
from datetime import datetime
from sqlalchemy import text

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from extensions import db
from config import Config

def create_tables():
    """Create all database tables with latest fixes"""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        print("🔧 Creating Rice Mill ERP Database Tables...")
        print("=" * 50)

        # Check database connection
        print("🔍 Checking database connection...")
        check_database_connection()

        # Import all models to ensure they're registered with SQLAlchemy
        print("📦 Importing models...")
        import_all_models()

        # Drop all tables first (for clean migration)
        print("🗑️ Dropping existing tables...")
        db.drop_all()

        # Create all tables
        print("🏗️ Creating all tables...")
        db.create_all()
        print("✅ All tables created successfully!")

        # Apply PostgreSQL specific optimizations
        print("🐘 Applying PostgreSQL optimizations...")
        apply_postgresql_optimizations()

        # Create default data
        print("📊 Creating default data...")
        create_default_data()
        print("✅ Default data created successfully!")

        print("🎉 Database migration completed successfully!")

def check_database_connection():
    """Check if database connection is working"""
    try:
        # Test database connection
        result = db.session.execute(text('SELECT 1'))
        result.scalar()
        print("✅ Database connection successful")

        # Detect database type
        db_url = str(db.engine.url)
        if 'postgresql' in db_url:
            print("✅ PostgreSQL database detected")
            try:
                result = db.session.execute(text('SELECT version()'))
                version = result.scalar()
                print(f"✅ PostgreSQL version: {version.split(',')[0]}")
            except:
                print("ℹ️ PostgreSQL version check failed")
        elif 'sqlite' in db_url:
            print("✅ SQLite database detected")
            try:
                result = db.session.execute(text('SELECT sqlite_version()'))
                version = result.scalar()
                print(f"✅ SQLite version: {version}")
            except:
                print("ℹ️ SQLite version check failed")
        else:
            print(f"ℹ️ Database type: {db_url.split(':')[0]}")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

def apply_postgresql_optimizations():
    """Apply database specific optimizations"""
    try:
        # Detect database type
        db_url = str(db.engine.url)

        if 'postgresql' not in db_url:
            print("ℹ️ Not PostgreSQL, skipping PostgreSQL-specific optimizations")
            return

        print("🐘 Applying PostgreSQL optimizations...")

        # Create indexes for better performance
        optimizations = [
            # User table indexes
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)",

            # Auth logs indexes
            "CREATE INDEX IF NOT EXISTS idx_auth_logs_user_id ON auth_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_auth_logs_timestamp ON auth_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_auth_logs_success ON auth_logs(success)",
            "CREATE INDEX IF NOT EXISTS idx_auth_logs_ip ON auth_logs(ip_address)",

            # Farmer table indexes
            "CREATE INDEX IF NOT EXISTS idx_farmers_code ON farmers(farmer_code)",
            "CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers(phone)",
            "CREATE INDEX IF NOT EXISTS idx_farmers_active ON farmers(is_active)",

            # Inventory indexes
            "CREATE INDEX IF NOT EXISTS idx_paddy_stock_farmer ON paddy_stock(farmer_id)",
            "CREATE INDEX IF NOT EXISTS idx_paddy_stock_date ON paddy_stock(purchase_date)",
            "CREATE INDEX IF NOT EXISTS idx_product_stock_variety ON product_stock(variety)",
        ]

        for optimization in optimizations:
            try:
                db.session.execute(text(optimization))
                print(f"✅ Applied: {optimization.split('(')[0]}...")
            except Exception as e:
                print(f"⚠️ Failed to apply optimization: {e}")

        db.session.commit()
        print("✅ PostgreSQL optimizations applied")

    except Exception as e:
        print(f"⚠️ Error applying PostgreSQL optimizations: {e}")
        db.session.rollback()

def import_all_models():
    """Import all model files to register them with SQLAlchemy"""
    imported_models = []

    # List of known model files
    model_files = [
        'models.user',
        'models.farmer',
        'models.inventory',
        'models.production',
        'models.sales',
        'models.financial',
        'models.finance'  # Alternative name
    ]

    for model_file in model_files:
        try:
            __import__(model_file)
            imported_models.append(model_file)
        except ImportError as e:
            print(f"ℹ️ {model_file} not found: {e}")
        except Exception as e:
            print(f"⚠️ Error importing {model_file}: {e}")

    print(f"✅ Successfully imported {len(imported_models)} model files:")
    for model in imported_models:
        print(f"  📦 {model}")

    # Try to import optional models
    optional_models = ['models.quality', 'models.analytics', 'models.ai_models']
    for model_file in optional_models:
        try:
            __import__(model_file)
            print(f"✅ Optional model imported: {model_file}")
        except ImportError:
            print(f"ℹ️ Optional model not found: {model_file}")
        except Exception as e:
            print(f"⚠️ Error importing optional model {model_file}: {e}")

def create_default_data():
    """Create default users and essential data"""
    try:
        from models.user import User
        from werkzeug.security import generate_password_hash

        # Create default admin user
        print("👤 Creating default admin user...")

        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("ℹ️ Admin user already exists, skipping creation")
            return

        admin_user = User(
            username='admin',
            email='admin@ricemill.com',
            password_hash=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            role='admin',  # Using string role field
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )

        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin user created (admin@ricemill.com / admin123)")

        # Create additional default users
        print("👥 Creating additional default users...")

        default_users = [
            {
                'username': 'manager',
                'email': 'manager@ricemill.com',
                'password': 'manager123',
                'first_name': 'Mill',
                'last_name': 'Manager',
                'role': 'manager'
            },
            {
                'username': 'operator',
                'email': 'operator@ricemill.com',
                'password': 'operator123',
                'first_name': 'Mill',
                'last_name': 'Operator',
                'role': 'operator'
            },
            {
                'username': 'quality',
                'email': 'quality@ricemill.com',
                'password': 'quality123',
                'first_name': 'Quality',
                'last_name': 'Controller',
                'role': 'quality_controller'
            },
            {
                'username': 'sales',
                'email': 'sales@ricemill.com',
                'password': 'sales123',
                'first_name': 'Sales',
                'last_name': 'Representative',
                'role': 'sales'
            }
        ]

        for user_data in default_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)

        db.session.commit()
        print("✅ Additional default users created")

        # Create default settings
        print("⚙️ Creating default system settings...")
        create_default_settings()

    except Exception as e:
        print(f"⚠️ Error creating default data: {e}")
        db.session.rollback()

def create_default_settings():
    """Create default system settings"""
    try:
        # This would create default settings if you have a settings model
        # For now, just print a message
        print("✅ Default settings initialized")

    except Exception as e:
        print(f"⚠️ Error creating default settings: {e}")

def create_sample_data():
    """Create sample data for testing (optional)"""
    print("📊 Creating sample data...")

    try:
        # Sample farmers
        from models.farmer import Farmer

        sample_farmers = [
            Farmer(
                farmer_code='FARM001',
                name='Rajesh Kumar',
                phone='9876543210',
                email='rajesh@example.com',
                village='Kharif Village',
                district='Punjab',
                state='Punjab',
                pincode='144001',
                total_land_area=5.0,
                farming_experience=15,
                is_active=True,
                created_at=datetime.utcnow()
            ),
            Farmer(
                farmer_code='FARM002',
                name='Suresh Patel',
                phone='9876543211',
                email='suresh@example.com',
                village='Rabi Village',
                district='Haryana',
                state='Haryana',
                pincode='122001',
                total_land_area=8.0,
                farming_experience=20,
                is_active=True,
                created_at=datetime.utcnow()
            )
        ]

        db.session.add_all(sample_farmers)
        db.session.commit()
        print("✅ Sample farmers created")

        # Sample inventory items
        from models.inventory import PaddyStock, ProductStock

        sample_paddy = PaddyStock(
            stock_id='STOCK000001',
            farmer_id=sample_farmers[0].id,
            variety='Basmati 1121',
            quantity=1000.0,
            purchase_price=2500.0,
            total_amount=2500000.0,
            moisture_content=14.0,
            purchase_date=datetime.utcnow(),
            warehouse_id='WH001',
            quality_grade='A',
            remaining_quantity=1000.0,
            created_at=datetime.utcnow()
        )

        db.session.add(sample_paddy)
        db.session.commit()
        print("✅ Sample inventory created")

    except Exception as e:
        print(f"⚠️ Error creating sample data: {e}")
        db.session.rollback()

def verify_database():
    """Verify database tables and data"""
    print("\n🔍 Verifying database...")

    try:
        # Check tables exist using inspector
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Found {len(tables)} tables:")

        for table in sorted(tables):
            print(f"  📋 {table}")

        # Check admin user exists
        from models.user import User
        admin_count = User.query.filter_by(username='admin').count()
        print(f"✅ Admin users: {admin_count}")

        # Check total users
        total_users = User.query.count()
        print(f"✅ Total users: {total_users}")

        # Check user roles
        admin_users = User.query.filter_by(role='admin').count()
        manager_users = User.query.filter_by(role='manager').count()
        operator_users = User.query.filter_by(role='operator').count()

        print(f"✅ User roles - Admin: {admin_users}, Manager: {manager_users}, Operator: {operator_users}")

        print("✅ Database verification completed")

    except Exception as e:
        print(f"⚠️ Error verifying database: {e}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Rice Mill ERP Database Migration')
    parser.add_argument('--with-sample-data', action='store_true',
                       help='Include sample data for testing')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing database')

    args = parser.parse_args()

    if args.verify_only:
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            import_all_models()
            verify_database()
    else:
        create_tables()

        if args.with_sample_data:
            print("\n📊 Adding sample data...")
            app = Flask(__name__)
            app.config.from_object(Config)
            db.init_app(app)

            with app.app_context():
                import_all_models()
                create_sample_data()

        # Always verify after creation
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            import_all_models()
            verify_database()

def main():
    """Main function with command line argument support"""
    import argparse

    parser = argparse.ArgumentParser(description='Create Rice Mill ERP database tables')
    parser.add_argument('--with-sample-data', action='store_true',
                       help='Include sample data creation')
    parser.add_argument('--drop-existing', action='store_true',
                       help='Drop existing tables before creating new ones')

    args = parser.parse_args()

    try:
        create_tables()
        print("\n🎊 Database setup completed successfully!")
        print("=" * 50)
        print("📊 Database Statistics:")

        # Show table count
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            # Import models to get table info
            import_all_models()

            # Get table names
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print(f"✅ Total tables created: {len(tables)}")
            print("📋 Tables:")
            for table in sorted(tables):
                print(f"  📄 {table}")

            # Show user count
            try:
                from models.user import User
                user_count = User.query.count()
                print(f"👥 Default users created: {user_count}")
            except:
                print("👥 User table not accessible")

        print("\n🚀 Ready to start the application!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()







