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
    run_query("""
        SELECT COUNT(*) as row_count FROM locations;
    """, "Locations Count")
    
    run_query("""
        SELECT COUNT(*) as row_count FROM water_samples;
    """, "Samples Count")

    run_query("""
        SELECT station_name, state, district, latitude, longitude, COUNT(*) as num_occurrences
        FROM locations
        GROUP BY station_name, state, district, latitude, longitude
        HAVING COUNT(*) > 1
        ORDER BY num_occurrences DESC
        LIMIT 10;
    """, "Duplicates in locations table based on geometry and name")
