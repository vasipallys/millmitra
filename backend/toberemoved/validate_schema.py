import psycopg2
import sys
from config import Config
from models.production import ProductionBatch
from sqlalchemy import inspect
from flask import Flask
from extensions import db

# Create Flask app to access model metadata
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    # Get model column names
    inspector = inspect(db.engine)
    model_columns = [column.name for column in ProductionBatch.__table__.columns]
    
    # Get actual database column names
    conn = psycopg2.connect(Config.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'production_batches'")
    db_columns = [row[0] for row in cur.fetchall()]
    conn.close()
    
    # Compare
    missing_in_db = set(model_columns) - set(db_columns)
    extra_in_db = set(db_columns) - set(model_columns)
    
    print('Schema Validation Report')
    print('=' * 30)
    print(f'Model columns: {len(model_columns)}')
    print(f'Database columns: {len(db_columns)}')
    
    if missing_in_db:
        print('\nMissing columns in database:')
        for col in missing_in_db:
            print(f'  - {col}')
    else:
        print('\nAll model columns exist in database')
    
    if extra_in_db:
        print('\nExtra columns in database:')
        for col in extra_in_db:
            print(f'  - {col}')
    else:
        print('\nNo extra columns in database')
    
    if not missing_in_db and not extra_in_db:
        print('\n\nSchema validation: PASSED')
    else:
        print('\n\nSchema validation: FAILED')
