from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if customers table exists
        result = db.session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'customers');"))
        exists = result.fetchone()[0]
        print(f"Customers table exists: {exists}")
        
        if exists:
            # Get count of records
            result = db.session.execute(text("SELECT COUNT(*) FROM customers;"))
            count = result.fetchone()[0]
            print(f"Number of customers: {count}")
        
    except Exception as e:
        print(f"Error checking customers table: {e}")
        import traceback
        traceback.print_exc()
