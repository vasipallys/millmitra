from app import create_app
from models.customers import Customer

app = create_app()

with app.app_context():
    try:
        # Check if customers table exists and has records
        customer_count = Customer.query.count()
        print(f"Customers table accessible. Total customers: {customer_count}")
        
        if customer_count > 0:
            # Get first customer as sample
            first_customer = Customer.query.first()
            print(f"Sample customer: {first_customer.business_name}")
            print(f"Customer ID: {first_customer.id}")
        else:
            print("No customers found in the database.")
            
    except Exception as e:
        print(f"Error accessing customers table: {e}")
        import traceback
        traceback.print_exc()
