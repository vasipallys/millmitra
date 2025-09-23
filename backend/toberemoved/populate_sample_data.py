import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from extensions import db
from app import create_app
from models.production import ProductionBatch, QualityTest
from models.financial import Transaction
from models.user import User

app = create_app()

with app.app_context():
    print("Populating database with sample data...")
    
    # Check if we have any users
    user_count = User.query.count()
    if user_count == 0:
        print("No users found. Please run the migration script first.")
        exit(1)
    
    # Get the first user as the creator
    user = User.query.first()
    user_id = user.id
    
    # Create sample production batches
    print("Creating sample production batches...")
    batch_numbers = ["BATCH001", "BATCH002", "BATCH003", "BATCH004", "BATCH005"]
    paddy_varieties = ["Basmati", "Sona Masuri", "Kolam", "Jeera Masuri", "Ponni"]
    
    for i, batch_num in enumerate(batch_numbers):
        # Create start and end times
        start_time = datetime.utcnow() - timedelta(days=30-i*5)
        end_time = start_time + timedelta(hours=random.randint(8, 12))
        
        batch = ProductionBatch(
            batch_number=batch_num,
            paddy_stock_id=1,  # Assuming a default paddy stock ID
            start_time=start_time,
            end_time=end_time,
            machine_id=f"MACHINE00{i+1}",
            operator_id=user_id,
            shift="morning" if i % 2 == 0 else "afternoon",
            paddy_input_quantity=random.uniform(1000, 2000),
            paddy_variety=random.choice(paddy_varieties),
            paddy_quality_grade=random.choice(["A", "B", "C"]),
            rice_output=random.uniform(600, 1200),
            broken_rice_output=random.uniform(50, 150),
            bran_output=random.uniform(100, 200),
            husk_output=random.uniform(150, 300),
            yield_percentage=random.uniform(60, 70),
            efficiency_percentage=random.uniform(85, 95),
            wastage_percentage=random.uniform(5, 15),
            output_quality_grade=random.choice(["A", "B", "C"]),
            moisture_content_output=random.uniform(12, 16),
            broken_percentage_output=random.uniform(2, 8),
            foreign_matter_output=random.uniform(0.5, 2.5),
            labor_cost=random.uniform(5000, 10000),
            energy_cost=random.uniform(2000, 5000),
            maintenance_cost=random.uniform(1000, 3000),
            total_production_cost=random.uniform(8000, 18000),
            created_by=user_id
        )
        
        # Calculate total output
        batch.total_output = batch.rice_output + batch.broken_rice_output + batch.bran_output + batch.husk_output
        
        db.session.add(batch)
    
    # Commit the batches
    db.session.commit()
    print(f"Created {len(batch_numbers)} production batches")
    
    # Create sample quality tests
    print("Creating sample quality tests...")
    test_ids = ["TEST001", "TEST002", "TEST003", "TEST004", "TEST005"]
    
    # Get the created batches
    batches = ProductionBatch.query.all()
    
    for i, test_id in enumerate(test_ids):
        if i < len(batches):
            batch = batches[i]
            test = QualityTest(
                test_id=test_id,
                batch_id=batch.id,
                sample_type="final_product",
                test_date=batch.end_time or (datetime.utcnow() - timedelta(days=30-i*5)),
                tested_by=user_id,
                test_method="standard_procedure",
                moisture_content=random.uniform(12, 16),
                foreign_matter=random.uniform(0.5, 2.5),
                broken_percentage=random.uniform(2, 8),
                chalky_percentage=random.uniform(1, 5),
                grain_length=random.uniform(6.5, 7.5),
                grain_width=random.uniform(2.0, 2.5),
                head_rice_percentage=random.uniform(70, 90),
                grade=random.choice(["A", "B", "C"]),
                grade_confidence=random.uniform(0.8, 0.95),
                status="completed",
                verified_by=user_id,
                verification_date=batch.end_time or (datetime.utcnow() - timedelta(days=30-i*5)),
                created_by=user_id
            )
            
            db.session.add(test)
    
    # Commit the quality tests
    db.session.commit()
    print(f"Created {len(test_ids)} quality tests")
    
    # Create sample transactions
    print("Creating sample transactions...")
    transaction_types = ["income", "expense"]
    categories = ["sales", "raw_materials", "labor", "maintenance", "utilities", "packaging"]
    descriptions = ["Rice sale to customer", "Paddy purchase", "Labor wages", "Machine maintenance", "Electricity bill", "Packaging materials"]
    
    for i in range(20):
        transaction_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        transaction_type = random.choice(transaction_types)
        category = random.choice(categories)
        description = random.choice(descriptions)
        
        # Generate amount based on type and category
        if transaction_type == "income":
            amount = random.uniform(50000, 200000) if "sale" in description.lower() else random.uniform(10000, 50000)
        else:
            if "paddy" in description.lower():
                amount = random.uniform(30000, 100000)
            elif "labor" in description.lower():
                amount = random.uniform(20000, 50000)
            elif "maintenance" in description.lower():
                amount = random.uniform(5000, 20000)
            elif "electricity" in description.lower():
                amount = random.uniform(8000, 15000)
            elif "packaging" in description.lower():
                amount = random.uniform(3000, 10000)
            else:
                amount = random.uniform(1000, 15000)
        
        transaction = Transaction(
            transaction_id=f"TXN{datetime.utcnow().strftime('%Y%m%d')}{i+1:03d}",
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            category=category,
            transaction_date=transaction_date,
            created_by=user_id
        )
        
        db.session.add(transaction)
    
    # Commit the transactions
    db.session.commit()
    print(f"Created 20 sample transactions")
    
    print("Sample data population completed successfully!")
