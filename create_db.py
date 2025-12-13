
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

DB_NAME = os.environ.get('DB_NAME', 'office_tools_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASSWORD', 'admin')
DB_HOST = os.environ.get('DB_HOST', 'localhost')

def create_db():
    conn = None
    try:
        # Connect to default 'postgres' db to create new db
        conn = psycopg2.connect(
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST, 
            dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {DB_NAME}...")
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created successfully.")
        else:
            print(f"Database {DB_NAME} already exists.")
            
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Please manually create it or verify credentials.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_db()
