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
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public';
    """, "List of Views")
    
    run_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'vw_station_wqi_summary' OR table_name = 'wawqi_results';
    """, "Columns in WAWQI tables/views")
