import os
import psycopg2
import pandas as pd

conn_str = "dbname='groundwater_quality' user='postgres' host='localhost' password='Nishant@2003' port='5432'"

def run_query(sql, description):
    print(f"\n=== {description} ===")
    try:
        with psycopg2.connect(conn_str) as conn:
            df = pd.read_sql_query(sql, conn)
            print(df.to_string())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    
    # 1. Station Identity Analysis (locations vs station names)
    run_query("""
        SELECT 
            COUNT(*) as total_locations,
            COUNT(DISTINCT station_name) as unique_station_names,
            COUNT(DISTINCT station_name || '-' || state || '-' || district) as unique_stations_with_geo
        FROM locations;
    """, "Station Identity Overview")

    run_query("""
        WITH name_counts AS (
            SELECT station_name, COUNT(location_id) as num_locations
            FROM locations
            GROUP BY station_name
        )
        SELECT num_locations, COUNT(station_name) as num_station_names
        FROM name_counts
        GROUP BY num_locations
        ORDER BY num_locations
        LIMIT 10;
    """, "Locations per Station Name Distribution")

    run_query("""
        WITH name_counts AS (
            SELECT station_name, COUNT(DISTINCT state) as num_states, COUNT(DISTINCT district) as num_districts, COUNT(DISTINCT concat(latitude, longitude)) as num_coords
            FROM locations
            GROUP BY station_name
        )
        SELECT 
            SUM(CASE WHEN num_states > 1 THEN 1 ELSE 0 END) as names_spanning_multiple_states,
            SUM(CASE WHEN num_districts > 1 THEN 1 ELSE 0 END) as names_spanning_multiple_districts,
            SUM(CASE WHEN num_coords > 1 THEN 1 ELSE 0 END) as names_with_multiple_coords
        FROM name_counts;
    """, "Station Name Consistency (Ambiguity)")

    # 2. Samples per location and station
    run_query("""
        WITH loc_samples AS (
            SELECT l.location_id, COUNT(s.sample_id) as sample_count
            FROM locations l
            LEFT JOIN water_samples s ON l.location_id = s.location_id
            GROUP BY l.location_id
        )
        SELECT 
            AVG(sample_count) as avg_samples_per_location,
            MAX(sample_count) as max_samples_per_location,
            SUM(CASE WHEN sample_count = 1 THEN 1 ELSE 0 END) as loc_with_1_sample,
            SUM(CASE WHEN sample_count = 2 THEN 1 ELSE 0 END) as loc_with_2_samples,
            SUM(CASE WHEN sample_count >= 3 THEN 1 ELSE 0 END) as loc_with_3_plus,
            SUM(CASE WHEN sample_count >= 5 THEN 1 ELSE 0 END) as loc_with_5_plus,
            SUM(CASE WHEN sample_count >= 10 THEN 1 ELSE 0 END) as loc_with_10_plus
        FROM loc_samples;
    """, "Samples per Location")

    # 3. Temporal Coverage
    run_query("""
        WITH loc_dates AS (
            SELECT 
                location_id, 
                MIN(sample_date) as first_date, 
                MAX(sample_date) as last_date,
                COUNT(DISTINCT EXTRACT(YEAR FROM sample_date)) as num_years
            FROM water_samples
            WHERE sample_date IS NOT NULL
            GROUP BY location_id
        )
        SELECT 
            MIN(first_date) as absolute_earliest,
            MAX(last_date) as absolute_latest,
            AVG(last_date - first_date) as avg_span_days,
            SUM(CASE WHEN num_years > 1 THEN 1 ELSE 0 END) as loc_with_multi_year
        FROM loc_dates;
    """, "Temporal Coverage Overview")

    # 4. Parameter Dominance Strategy (Checking existing vw_wqi_samples logic)
    run_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'vw_wqi_samples';
    """, "Existing vw_wqi_samples Structure")
