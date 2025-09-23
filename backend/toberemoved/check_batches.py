import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from extensions import db
from app import create_app
from models.production import ProductionBatch

app = create_app()

with app.app_context():
    print("Checking production batches...")
    
    # Get all batches
    batches = ProductionBatch.query.all()
    
    for batch in batches:
        print(f"Batch ID: {batch.id}")
        print(f"Batch Number: {batch.batch_number}")
        print(f"Start Time: {batch.start_time}")
        print(f"Rice Output: {batch.rice_output}")
        print("---")
    
    print(f"Total batches: {len(batches)}")
