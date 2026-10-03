import os
from scripts.etl.loader import get_connection

def main():
    conn = get_connection()
    if not conn:
        print("Could not connect to database.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            
            schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', '01_schema.sql')
            with open(schema_path, 'r') as f:
                cur.execute(f.read())
        conn.commit()
        print("Schema reset successfully.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
