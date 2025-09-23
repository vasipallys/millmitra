import psycopg2

try:
    # Try to connect directly to the database
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="rice_mill_erp",
        user="postgres",
        password="siva"
    )
    print("Successfully connected to database!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Failed to connect to database: {e}")
