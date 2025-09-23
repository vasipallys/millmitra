import psycopg2
import sys
from config import Config

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(Config.DATABASE_URL)
    cur = conn.cursor()
    
    # Check if efficiency_score column exists
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'production_batches' AND column_name = 'efficiency_score'")
    result = cur.fetchone()
    
    if result:
        print('efficiency_score column already exists')
    else:
        print('Adding efficiency_score column to production_batches table...')
        # Add the missing column
        cur.execute("ALTER TABLE production_batches ADD COLUMN efficiency_score FLOAT")
        conn.commit()
        print('Successfully added efficiency_score column')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
