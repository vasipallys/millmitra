import psycopg2
import sys
from config import Config

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(Config.DATABASE_URL)
    cur = conn.cursor()
    
    # Get column names from production_batches table
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'production_batches'")
    columns = cur.fetchall()
    
    print('Current columns in production_batches table:')
    for col in columns:
        print(f'  - {col[0]}')
    
    # Check specifically for efficiency_score column
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'production_batches' AND column_name = 'efficiency_score'")
    result = cur.fetchone()
    
    if result:
        print('\n✓ efficiency_score column exists')
    else:
        print('\n✗ efficiency_score column is missing')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
