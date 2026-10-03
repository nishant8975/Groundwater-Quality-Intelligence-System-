import os
import glob
import time
from scripts.etl.config import RAW_DATA_DIR
from scripts.etl.run_etl import ETLRunner
from scripts.etl.loader import get_connection

class TargetedETLRunner(ETLRunner):
    def __init__(self, target_files=None):
        super().__init__()
        self.target_files = target_files

    def discover_files(self):
        if self.target_files:
            return [os.path.join(RAW_DATA_DIR, f) for f in self.target_files]
        return super().discover_files()

def print_db_counts():
    conn = get_connection()
    if not conn:
        print("Failed to connect to DB for counts.")
        return
    try:
        with conn.cursor() as cur:
            tables = ['source_datasets', 'locations', 'parameters', 'water_samples', 'sample_parameter_values']
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                count = cur.fetchone()[0]
                print(f"  {t.ljust(25)} : {count}")
    finally:
        conn.close()

def main():
    print("--- 1. SINGLE-DATASET TEST ---")
    t0 = time.time()
    runner = TargetedETLRunner(['Puducherry.csv'])
    runner.run()
    t1 = time.time()
    print(f"Single dataset runtime: {t1-t0:.2f}s")
    print_db_counts()
    
    print("\n--- 2. MULTI-STATE TEST ---")
    t0 = time.time()
    # Pick a few distinct ones
    runner = TargetedETLRunner(['Chandigarh.csv', 'Tripura.csv', 'Andaman_Nicobar.csv'])
    runner.run()
    t1 = time.time()
    print(f"Multi-state runtime: {t1-t0:.2f}s")
    print_db_counts()

    print("\n--- 3. FULL 30-DATASET ETL ---")
    t0 = time.time()
    runner = TargetedETLRunner() # All files
    runner.run()
    t1 = time.time()
    print(f"Full ETL runtime: {t1-t0:.2f}s")
    print_db_counts()

    print("\n--- 4. IDEMPOTENCY TEST ---")
    print("Re-running ETL with all files...")
    runner = TargetedETLRunner()
    runner.run()
    print("DB Counts after idempotency run (should be exactly the same as above):")
    print_db_counts()
    
    print("\n--- 5. PROVENANCE & ANOMALIES VALIDATION ---")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 6 non-numeric anomalies
            cur.execute("""
                SELECT sd.filename, ws.source_row_index, p.canonical_name, spv.raw_value_string, spv.data_quality_flag
                FROM sample_parameter_values spv
                JOIN water_samples ws ON spv.sample_id = ws.sample_id
                JOIN source_datasets sd ON ws.source_dataset_id = sd.dataset_id
                JOIN parameters p ON spv.parameter_id = p.parameter_id
                WHERE spv.data_quality_flag = 'INVALID_NUMERIC'
                LIMIT 10;
            """)
            anomalies = cur.fetchall()
            print(f"\nNon-numeric anomalies found: {len(anomalies)}")
            for a in anomalies:
                print(f"  File: {a[0]}, Row: {a[1]}, Param: {a[2]}, Raw: '{a[3]}', DQ: {a[4]}")
                
            # Placeholders
            cur.execute("""
                SELECT COUNT(*) FROM sample_parameter_values WHERE is_placeholder = True;
            """)
            plc = cur.fetchone()[0]
            print(f"\nPlaceholder values (e.g. ND, -) count: {plc}")
            
    finally:
        conn.close()

if __name__ == '__main__':
    main()
