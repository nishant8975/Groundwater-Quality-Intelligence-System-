import os
import psycopg2
from psycopg2.extras import execute_values
from scripts.etl.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        # Depending on environment, DB might not be available
        print(f"Database Connection Error: {e}")
        return None

def initialize_schema():
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='source_datasets';")
            if cur.fetchone():
                return True
            
            schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', '01_schema.sql')
            with open(schema_path, 'r') as f:
                cur.execute(f.read())
            conn.commit()
            return True
    except Exception as e:
        print(f"Schema initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def setup_parameters():
    from scripts.etl.mappings import PARAMETER_MAPPINGS
    conn = get_connection()
    if not conn:
        return False
    
    unique_params = {}
    for alias, (canonical_name, display_name, unit) in PARAMETER_MAPPINGS.items():
        if canonical_name not in unique_params:
            unique_params[canonical_name] = (display_name, unit)
            
    insert_query = """
        INSERT INTO parameters (canonical_name, display_name, default_unit)
        VALUES %s
        ON CONFLICT (canonical_name) DO NOTHING
    """
    values = [(k, v[0], v[1]) for k, v in unique_params.items()]
    
    try:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, values)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error setting up parameters: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_parameter_ids():
    conn = get_connection()
    if not conn:
        return {}
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT canonical_name, parameter_id FROM parameters")
            return {row[0]: row[1] for row in cur.fetchall()}
    except Exception as e:
        print(f"Error getting parameter ids: {e}")
        return {}
    finally:
        conn.close()

def is_dataset_loaded(filename):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT dataset_id FROM source_datasets WHERE filename = %s", (filename,))
            res = cur.fetchone()
            return res is not None
    except Exception as e:
        return False
    finally:
        conn.close()

def register_dataset(filename, state, row_count, batch_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO source_datasets (filename, state_inferred, row_count, ingestion_batch_id)
                VALUES (%s, %s, %s, %s) RETURNING dataset_id
            """, (filename, state, row_count, batch_id))
            dataset_id = cur.fetchone()[0]
        conn.commit()
        return dataset_id
    except Exception as e:
        print(f"Error registering dataset {filename}: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def delete_dataset(dataset_id):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM water_samples WHERE source_dataset_id = %s", (dataset_id,))
            cur.execute("DELETE FROM locations WHERE source_dataset_id = %s", (dataset_id,))
            cur.execute("DELETE FROM source_datasets WHERE dataset_id = %s", (dataset_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting dataset {dataset_id}: {e}")
        conn.rollback()
    finally:
        conn.close()
