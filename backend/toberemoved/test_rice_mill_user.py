import psycopg2
import sys

# Test if we can connect with the rice_mill_user
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="rice_mill_erp",
        user="rice_mill_user",
        password="rice_mill_password"  # Using the password from config.py
    )
    print("Successfully connected with rice_mill_user")
    conn.close()
except Exception as e:
    print(f"Failed to connect with rice_mill_user: {e}")

# Test if we can connect with the postgres user
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="rice_mill_erp",
        user="postgres",
        password="siva"  # Using the password from config.py
    )
    print("Successfully connected with postgres user")
    conn.close()
except Exception as e:
    print(f"Failed to connect with postgres user: {e}")
