import os
from scripts.etl.loader import get_connection

def main():
    conn = get_connection()
    if not conn:
        print("Could not connect to DB.")
        return
        
    try:
        with conn.cursor() as cur:
            # 1. Duplicate Analysis
            print("--- 1. DUPLICATE ANALYSIS ---")
            # Potential duplicate samples (Station + Date)
            cur.execute("""
                SELECT l.station_name, ws.sample_date, count(*) as cnt
                FROM water_samples ws
                JOIN locations l ON ws.location_id = l.location_id
                WHERE l.station_name IS NOT NULL AND ws.sample_date IS NOT NULL
                GROUP BY l.station_name, ws.sample_date
                HAVING count(*) > 1
                ORDER BY cnt DESC;
            """)
            dup_samples = cur.fetchall()
            affected_samples = sum(d[2] for d in dup_samples)
            print(f"Potential duplicate sample groups: {len(dup_samples)}")
            print(f"Affected water samples: {affected_samples}")
            
            if dup_samples:
                print(f"Example groups: {dup_samples[:5]}")
            
            # Duplicate parameter observations (Station + Date + Parameter)
            cur.execute("""
                SELECT l.station_name, ws.sample_date, p.canonical_name, count(*) as cnt
                FROM sample_parameter_values spv
                JOIN water_samples ws ON spv.sample_id = ws.sample_id
                JOIN locations l ON ws.location_id = l.location_id
                JOIN parameters p ON spv.parameter_id = p.parameter_id
                WHERE l.station_name IS NOT NULL AND ws.sample_date IS NOT NULL
                GROUP BY l.station_name, ws.sample_date, p.canonical_name
                HAVING count(*) > 1
            """)
            dup_params = cur.fetchall()
            affected_params = sum(d[3] for d in dup_params)
            print(f"Potential duplicate parameter observations: {affected_params} across {len(dup_params)} groups.")
            
            # Datasets containing duplicates
            cur.execute("""
                SELECT DISTINCT sd.filename
                FROM water_samples ws
                JOIN locations l ON ws.location_id = l.location_id
                JOIN source_datasets sd ON ws.source_dataset_id = sd.dataset_id
                WHERE l.station_name IS NOT NULL AND ws.sample_date IS NOT NULL
                AND EXISTS (
                    SELECT 1 FROM water_samples ws2 
                    JOIN locations l2 ON ws2.location_id = l2.location_id
                    WHERE l2.station_name = l.station_name 
                      AND ws2.sample_date = ws.sample_date 
                      AND ws2.sample_id != ws.sample_id
                )
            """)
            dup_datasets = [row[0] for row in cur.fetchall()]
            print(f"Datasets containing potential duplicates: {len(dup_datasets)}")

            # 2. Location Cardinality
            print("\n--- 2. LOCATION CARDINALITY ---")
            cur.execute("SELECT count(*) FROM locations")
            total_locs = cur.fetchone()[0]
            print(f"Total location records: {total_locs}")
            
            cur.execute("SELECT count(DISTINCT station_name) FROM locations")
            distinct_stations = cur.fetchone()[0]
            print(f"Distinct station names: {distinct_stations}")
            
            cur.execute("""
                SELECT station_name, count(*) as cnt
                FROM locations
                WHERE station_name IS NOT NULL
                GROUP BY station_name
                HAVING count(*) > 1
            """)
            repeated_locs = cur.fetchall()
            print(f"Potential duplicate location entities (same station_name): {len(repeated_locs)}")
            print("Note: The ETL maps 1 location record per source row, preserving original geography context. Same name != same physical location without proper ID.")

            # 3. Sample Cardinality
            print("\n--- 3. SAMPLE CARDINALITY ---")
            cur.execute("SELECT sum(row_count) FROM source_datasets")
            source_rows = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM water_samples")
            total_samples = cur.fetchone()[0]
            print(f"Source rows: {source_rows}")
            print(f"Water samples: {total_samples}")
            print(f"Source rows without sample: {source_rows - total_samples}")

            # 4. Parameter Observations
            print("\n--- 4. PARAMETER OBSERVATIONS ---")
            cur.execute("""
                SELECT sd.filename, sd.row_count, count(spv.parameter_id)
                FROM source_datasets sd
                LEFT JOIN water_samples ws ON sd.dataset_id = ws.source_dataset_id
                LEFT JOIN sample_parameter_values spv ON ws.sample_id = spv.sample_id
                GROUP BY sd.filename, sd.row_count
                ORDER BY sd.filename
            """)
            print("Dataset | Source Rows | Parameter Observations")
            total_obs = 0
            for row in cur.fetchall():
                total_obs += row[2]
                print(f"{row[0]} | {row[1]} | {row[2]}")
            print(f"Total parameter observations: {total_obs}")

            # 5. Non-Numeric Anomalies
            print("\n--- 5. NON-NUMERIC ANOMALIES ---")
            cur.execute("""
                SELECT sd.filename, ws.source_row_index, p.canonical_name, spv.raw_value_string, spv.numeric_value, spv.data_quality_flag
                FROM sample_parameter_values spv
                JOIN water_samples ws ON spv.sample_id = ws.sample_id
                JOIN source_datasets sd ON ws.source_dataset_id = sd.dataset_id
                JOIN parameters p ON spv.parameter_id = p.parameter_id
                WHERE spv.data_quality_flag = 'INVALID_NUMERIC'
            """)
            anomalies = cur.fetchall()
            for a in anomalies:
                print(f"Dataset: {a[0]}, Row: {a[1]}, Param: {a[2]}, Raw: '{a[3]}', Numeric: {a[4]}, Flag: {a[5]}")

            # 6. Placeholders
            print("\n--- 6. PLACEHOLDERS ---")
            cur.execute("""
                SELECT raw_value_string, count(*) 
                FROM sample_parameter_values 
                WHERE numeric_value IS NULL AND raw_value_string IS NOT NULL AND TRIM(raw_value_string) != ''
                AND data_quality_flag != 'INVALID_NUMERIC'
                GROUP BY raw_value_string
                ORDER BY count(*) DESC
                LIMIT 20
            """)
            placeholders = cur.fetchall()
            
            cur.execute("""
                SELECT count(*) FROM sample_parameter_values 
                WHERE numeric_value IS NULL AND raw_value_string IS NOT NULL AND TRIM(raw_value_string) != ''
                AND data_quality_flag != 'INVALID_NUMERIC'
            """)
            total_placeholders = cur.fetchone()[0]
            
            print(f"Raw placeholder occurrences: {total_placeholders}")
            print("Examples:", placeholders[:10])
            print("Stored raw values: Preserved as string")
            print("Stored numeric values: NULL")
            print("Quality classification: Missing/NULL handled naturally.")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
