import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from extensions import db
from app import create_app
from models.production import ProductionBatch, QualityTest
from models.financial import Transaction
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("Checking database connectivity and required tables...")
    
    # Check if we can query ProductionBatch table
    try:
        # Try to get count of production batches
        batch_count = ProductionBatch.query.count()
        print(f"ProductionBatch table accessible. Total batches: {batch_count}")
        
        # Try to get recent batches
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_batches = ProductionBatch.query.filter(
            ProductionBatch.start_time >= thirty_days_ago
        ).all()
        print(f"Recent batches (30 days): {len(recent_batches)}")
        
    except Exception as e:
        print(f"Error querying ProductionBatch table: {e}")
    
    # Check if we can query QualityTest table
    try:
        # Try to get count of quality tests
        test_count = QualityTest.query.count()
        print(f"QualityTest table accessible. Total tests: {test_count}")
        
        # Try to get recent tests
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_tests = QualityTest.query.filter(
            QualityTest.test_date >= thirty_days_ago
        ).all()
        print(f"Recent quality tests (30 days): {len(recent_tests)}")
        
    except Exception as e:
        print(f"Error querying QualityTest table: {e}")
    
    # Check if we can query Transaction table
    try:
        # Try to get count of transactions
        transaction_count = Transaction.query.count()
        print(f"Transaction table accessible. Total transactions: {transaction_count}")
        
        # Try to get recent transactions
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_transactions = Transaction.query.filter(
            Transaction.transaction_date >= thirty_days_ago
        ).all()
        print(f"Recent transactions (30 days): {len(recent_transactions)}")
        
    except Exception as e:
        print(f"Error querying Transaction table: {e}")
    
    print("Database check completed.")
