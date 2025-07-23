"""
Create farmer_edit_requests table
Migration to add farmer edit verification system
"""

from extensions import db
from models.farmer_edit_request import FarmerEditRequest

def create_farmer_edit_requests_table():
    """Create the farmer_edit_requests table"""
    try:
        # Create the table
        db.create_all()
        print("✅ farmer_edit_requests table created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating farmer_edit_requests table: {str(e)}")
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    with app.app_context():
        success = create_farmer_edit_requests_table()
        if success:
            print("✅ Migration completed successfully")
        else:
            print("❌ Migration failed")
