import sys
import os
from datetime import datetime
import random

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from extensions import db
from app import create_app
# Import the Customer model from the sales module
from models.sales import Customer

app = create_app()

with app.app_context():
    print("Adding sample customer data...")
    
    # Check if we already have customers
    customer_count = Customer.query.count()
    if customer_count > 0:
        print(f"Found {customer_count} existing customers. Skipping sample data creation.")
        exit(0)
    
    # Sample customer data - aligned with Customer model in models/sales.py
    sample_customers = [
        {
            'name': 'Premium Rice Distributors',
            'contact_person': 'Rajesh Kumar',
            'phone': '+91 98765 43210',
            'email': 'rajesh@premiumrice.com',
            'address': '123 Main Street',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'pincode': '500001',
            'country': 'India',
            'business_name': 'Premium Rice Distributors',
            'credit_limit': 100000,
            'outstanding_amount': 25000,
            'payment_terms': '30_days',
            'total_orders': 15,
            'total_order_value': 5000000,
            'average_order_value': 333333,
            'loyalty_score': 8.5,
            'price_sensitivity': 0.2,
            'credit_rating': 'AAA',
            'risk_category': 'low',
            'payment_behavior_score': 9.5,
            'is_active': True,
            'last_order_date': datetime(2024, 3, 10),
            'lifetime_value': 150000,
            'churn_probability': 0.1
        },
        {
            'name': 'Southern Restaurant Group',
            'contact_person': 'Priya Sharma',
            'phone': '+91 98765 43211',
            'email': 'priya@southernrestaurants.com',
            'address': '456 Commercial Road',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'pincode': '600001',
            'country': 'India',
            'business_name': 'Southern Restaurant Group',
            'credit_limit': 50000,
            'outstanding_amount': 12000,
            'payment_terms': '15_days',
            'total_orders': 8,
            'total_order_value': 2500000,
            'average_order_value': 312500,
            'loyalty_score': 7.2,
            'price_sensitivity': 0.4,
            'credit_rating': 'AA',
            'risk_category': 'low',
            'payment_behavior_score': 8.2,
            'is_active': True,
            'last_order_date': datetime(2024, 3, 5),
            'lifetime_value': 75000,
            'churn_probability': 0.25
        },
        {
            'name': 'Local Supermarket Chain',
            'contact_person': 'Amit Patel',
            'phone': '+91 98765 43212',
            'email': 'amit@localsupermarket.com',
            'address': '789 Market Street',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'pincode': '560001',
            'country': 'India',
            'business_name': 'Local Supermarket Chain',
            'credit_limit': 25000,
            'outstanding_amount': 5000,
            'payment_terms': 'immediate',
            'total_orders': 5,
            'total_order_value': 1500000,
            'average_order_value': 300000,
            'loyalty_score': 6.8,
            'price_sensitivity': 0.6,
            'credit_rating': 'A',
            'risk_category': 'medium',
            'payment_behavior_score': 7.9,
            'is_active': True,
            'last_order_date': datetime(2024, 3, 8),
            'lifetime_value': 50000,
            'churn_probability': 0.3
        }
    ]
    
    # Add customers to database
    for i, customer_data in enumerate(sample_customers):
        customer = Customer(
            customer_code=f'CUST{str(i+1).zfill(3)}',
            **customer_data
        )
        db.session.add(customer)
    
    db.session.commit()
    print(f"Successfully added {len(sample_customers)} sample customers to the database.")
