import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'groundwater_quality')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', '')

    # 1. Check PostgreSQL Connectivity & Create Database if needed
    try:
        # Connect to the default 'postgres' database for administrative tasks
        conn_admin = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname='postgres', # Connect to default db
            user=db_user,
            password=db_password
        )
        conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur_admin = conn_admin.cursor()
        
        print("PostgreSQL connection: SUCCESS")

        # Check if database exists
        cur_admin.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cur_admin.fetchone()
        
        if not exists:
            cur_admin.execute(f"CREATE DATABASE {db_name}")
            print(f"Database creation: Created")
        else:
            print(f"Database creation: Already existed")
            
        cur_admin.close()
        conn_admin.close()

    except Exception as e:
        print(f"PostgreSQL connection: Failed ({type(e).__name__})")
        return

    # 2. Connect to the target database and run schema
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cur = conn.cursor()
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', '01_schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        cur.execute(schema_sql)
        conn.commit()
        print("Schema execution: SUCCESS")
        
        # Verify tables created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables count: {len(tables)}")
        print(f"Tables list: {', '.join(tables)}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Schema execution: Failed ({type(e).__name__}: {e})")

if __name__ == '__main__':
    main()
