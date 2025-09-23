import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from models.production import ProductionBatch
from extensions import db

app = create_app()

with app.app_context():
    # Test that ProductionBatch model has efficiency_score attribute
    batch = ProductionBatch()
    batch.efficiency_score = 95.5
    print(f"Successfully set efficiency_score: {batch.efficiency_score}")
    
    # Test dashboard service
    from services.dashboard_service import SmartDashboardService
    dashboard = SmartDashboardService()
    print("Dashboard service created successfully")
    
    print("All tests passed!")
