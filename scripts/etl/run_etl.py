import os
import glob
import pandas as pd
import uuid
import datetime
from psycopg2.extras import execute_values
from scripts.etl.config import RAW_DATA_DIR
from scripts.etl.mappings import PARAMETER_MAPPINGS, GEO_MAPPINGS
from scripts.etl.normalization import parse_numeric, parse_date, validate_coordinates
from scripts.etl.loader import get_connection, initialize_schema, setup_parameters, get_parameter_ids, is_dataset_loaded, register_dataset, delete_dataset

class ETLRunner:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        self.db_available = get_connection() is not None
        self.parameter_ids = {}
        
        self.stats = {
            'total_files': 0,
            'total_source_rows': 0,
            'loaded_rows': 0,
            'rejected_rows': 0,
            'samples_inserted': 0,
            'parameter_observations_inserted': 0,
            'locations_inserted': 0,
            'missing_dates': 0,
            'invalid_dates': 0,
            'missing_coordinates': 0,
            'invalid_coordinates': 0,
            'placeholder_values': 0,
            'non_numeric_values': 0,
            'potential_duplicates': 0
        }
        
        self.state_stats = {}

    def discover_files(self):
        pattern = os.path.join(RAW_DATA_DIR, '*.csv')
        return glob.glob(pattern)

    def run(self):
        print(f"Starting ETL Pipeline. Batch ID: {self.batch_id}")
        if self.db_available:
            print("Database connected. Initializing schema and parameters...")
            initialize_schema()
            setup_parameters()
            self.parameter_ids = get_parameter_ids()
        else:
            print("DATABASE EXECUTION BLOCKED. Running in validation-only mode.")
            
        files = self.discover_files()
        self.stats['total_files'] = len(files)
        
        for f in files:
            self.process_file(f)
            
        self.generate_reports()

    def process_file(self, filepath):
        filename = os.path.basename(filepath)
        state = filename.replace('.csv', '').replace('_', ' ')
        print(f"Processing {filename} ({state})...")
        
        try:
            df = pd.read_csv(filepath, keep_default_na=False)
        except Exception as e:
            print(f"Failed to read {filename}: {e}")
            return
            
        row_count = len(df)
        self.stats['total_source_rows'] += row_count
        
        self.state_stats[state] = {
            'source_rows': row_count,
            'loaded_rows': 0,
            'rejected_rows': 0,
            'missing_dates': 0,
            'invalid_dates': 0,
            'missing_coordinates': 0,
            'invalid_coordinates': 0,
            'placeholder_values': 0,
            'numeric_values': 0,
            'potential_duplicates': 0
        }
        
        if self.db_available and is_dataset_loaded(filename):
            print(f"Dataset {filename} already loaded. Skipping to ensure idempotency.")
            return
            
        dataset_id = -1
        if self.db_available:
            dataset_id = register_dataset(filename, state, row_count, self.batch_id)
            if dataset_id is None:
                print(f"Failed to register dataset {filename}")
                return
        
        # Analyze columns
        cols = [c for c in df.columns if not c.startswith('Unnamed:')]
        
        # Determine geo columns available
        geo_cols = {}
        for c in cols:
            clower = c.lower().strip()
            if clower in GEO_MAPPINGS:
                geo_cols[GEO_MAPPINGS[clower]] = c
                
        # Determine parameter columns available
        param_cols = {}
        for c in cols:
            clower = c.lower().strip()
            if clower in PARAMETER_MAPPINGS:
                canonical = PARAMETER_MAPPINGS[clower][0]
                param_cols[canonical] = c
                
        locations_data = []
        samples_data = []
        param_values_data = []
        
        conn = get_connection() if self.db_available else None
        cursor = conn.cursor() if conn else None
        
        try:
            for idx, row in df.iterrows():
                source_row_index = idx + 2 # 1-based, plus header
                
                # Geography
                lat = None
                lon = None
                if 'latitude' in geo_cols:
                    lat_raw, _, _, _ = parse_numeric(row.get(geo_cols['latitude']))
                    lat = lat_raw
                if 'longitude' in geo_cols:
                    lon_raw, _, _, _ = parse_numeric(row.get(geo_cols['longitude']))
                    lon = lon_raw
                    
                is_valid_coord, coord_flag = validate_coordinates(lat, lon)
                if coord_flag == "MISSING":
                    self.stats['missing_coordinates'] += 1
                    self.state_stats[state]['missing_coordinates'] += 1
                elif coord_flag != "VALID":
                    self.stats['invalid_coordinates'] += 1
                    self.state_stats[state]['invalid_coordinates'] += 1
                
                # Build location tuple
                loc_state = row.get(geo_cols.get('state')) if 'state' in geo_cols else state
                loc_tuple = (
                    dataset_id,
                    loc_state,
                    row.get(geo_cols.get('state_lgd_code')),
                    row.get(geo_cols.get('district')),
                    row.get(geo_cols.get('district_lgd_code')),
                    row.get(geo_cols.get('tehsil')),
                    row.get(geo_cols.get('block')),
                    row.get(geo_cols.get('village')),
                    row.get(geo_cols.get('station_name')),
                    row.get(geo_cols.get('agency')),
                    lat,
                    lon,
                    is_valid_coord
                )
                
                # Insert location if DB available
                location_id = -1
                if self.db_available:
                    cursor.execute("""
                        INSERT INTO locations (
                            source_dataset_id, state, state_lgd_code, district, district_lgd_code,
                            tehsil, block, village, station_name, agency, latitude, longitude, coordinate_validity_flag
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING location_id
                    """, loc_tuple)
                    location_id = cursor.fetchone()[0]
                    self.stats['locations_inserted'] += 1
                
                # Date
                raw_date = row.get(geo_cols.get('sample_date')) if 'sample_date' in geo_cols else None
                parsed_date, date_flag = parse_date(raw_date)
                
                if date_flag == "MISSING":
                    self.stats['missing_dates'] += 1
                    self.state_stats[state]['missing_dates'] += 1
                elif date_flag == "INVALID_DATE":
                    self.stats['invalid_dates'] += 1
                    self.state_stats[state]['invalid_dates'] += 1
                
                # Insert Sample
                sample_id = -1
                if self.db_available:
                    cursor.execute("""
                        INSERT INTO water_samples (
                            location_id, source_dataset_id, source_row_index, sample_date, raw_date_string, date_validity_flag
                        ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING sample_id
                    """, (location_id, dataset_id, source_row_index, parsed_date, str(raw_date) if raw_date is not None else None, parsed_date is not None))
                    sample_id = cursor.fetchone()[0]
                    self.stats['samples_inserted'] += 1
                    
                # Parameters
                row_params_batch = []
                for canonical_name, source_col in param_cols.items():
                    val = row.get(source_col)
                    val_str = str(val).strip() if pd.notna(val) else ""
                    if pd.isna(val) or val_str == "":
                        continue # Sparse representation
                        
                    num_val, is_missing, is_placeholder, dq_flag = parse_numeric(val)
                    
                    if is_placeholder:
                        self.stats['placeholder_values'] += 1
                        self.state_stats[state]['placeholder_values'] += 1
                    elif dq_flag == "INVALID_NUMERIC":
                        self.stats['non_numeric_values'] += 1
                        # self.state_stats[state]['non_numeric_values'] += 1
                    elif dq_flag == "VALID_NUMERIC":
                        self.state_stats[state]['numeric_values'] += 1
                    
                    param_id = self.parameter_ids.get(canonical_name, -1)
                    unit = PARAMETER_MAPPINGS.get(source_col.lower().strip(), ("", "", ""))[2]
                    
                    if self.db_available and param_id != -1:
                        row_params_batch.append((
                            sample_id, param_id, num_val, str(val), unit, is_missing, is_placeholder, dq_flag
                        ))
                
                if self.db_available and row_params_batch:
                    execute_values(cursor, """
                        INSERT INTO sample_parameter_values (
                            sample_id, parameter_id, numeric_value, raw_value_string, unit, is_missing, is_placeholder, data_quality_flag
                        ) VALUES %s
                    """, row_params_batch)
                    self.stats['parameter_observations_inserted'] += len(row_params_batch)
                
                self.stats['loaded_rows'] += 1
                self.state_stats[state]['loaded_rows'] += 1
                
            if self.db_available:
                conn.commit()
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            if self.db_available:
                conn.rollback()
                delete_dataset(dataset_id)
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def generate_reports(self):
        docs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        dq_report_path = os.path.join(docs_dir, 'ETL_DATA_QUALITY_REPORT.md')
        with open(dq_report_path, 'w') as f:
            f.write("# ETL Data Quality Report\n\n")
            f.write("## Overall Statistics\n")
            for k, v in self.stats.items():
                f.write(f"- **{k}**: {v}\n")
                
            f.write("\n## State Statistics\n")
            f.write("| State | Source Rows | Loaded | Rejected | Missing Dates | Invalid Dates | Missing Coords | Invalid Coords | Placeholders | Numerics |\n")
            f.write("|---|---|---|---|---|---|---|---|---|---|\n")
            for state, st in self.state_stats.items():
                f.write(f"| {state} | {st['source_rows']} | {st['loaded_rows']} | {st['rejected_rows']} | {st['missing_dates']} | {st['invalid_dates']} | {st['missing_coordinates']} | {st['invalid_coordinates']} | {st['placeholder_values']} | {st['numeric_values']} |\n")
        
        dup_report_path = os.path.join(docs_dir, 'ETL_DUPLICATE_REPORT.md')
        with open(dup_report_path, 'w') as f:
            f.write("# ETL Duplicate Analysis Report\n\n")
            f.write("Note: This phase does not actively deduplicate records, to preserve raw file integrity. ")
            f.write("Duplicates will be aggregated in Phase 4 via BI-level dedup.\n\n")
            if self.db_available:
                # Query actual duplicates
                try:
                    conn = get_connection()
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT l.station_name, ws.sample_date, count(*) 
                            FROM water_samples ws 
                            JOIN locations l ON ws.location_id = l.location_id
                            WHERE l.station_name IS NOT NULL AND ws.sample_date IS NOT NULL
                            GROUP BY l.station_name, ws.sample_date
                            HAVING count(*) > 1
                            LIMIT 50
                        """)
                        dups = cur.fetchall()
                        f.write("## Potential Duplicates Sample\n")
                        f.write("| Station | Date | Count |\n|---|---|---|\n")
                        for d in dups:
                            f.write(f"| {d[0]} | {d[1]} | {d[2]} |\n")
                    conn.close()
                except Exception as e:
                    f.write(f"Could not generate duplicate analysis: {e}\n")
            else:
                f.write("Database not connected; skipping exact duplicate querying.\n")
                
        print(f"ETL Complete. Loaded {self.stats['loaded_rows']} out of {self.stats['total_source_rows']} rows.")

if __name__ == '__main__':
    runner = ETLRunner()
    runner.run()
