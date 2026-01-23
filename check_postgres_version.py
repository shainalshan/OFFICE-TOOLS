
import psycopg2
import os

DB_NAME = os.environ.get('DB_NAME', 'office_tools_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASSWORD', 'admin')
DB_HOST = os.environ.get('DB_HOST', 'localhost')

def check_version():
    try:
        conn = psycopg2.connect(
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST, 
            dbname=DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL Version: {version}")
        
    except Exception as e:
        print(f"Error checking version: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_version()
