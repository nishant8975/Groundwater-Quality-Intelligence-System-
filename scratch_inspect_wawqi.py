import psycopg2
import pandas as pd
import json

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
        SELECT parameters_used
        FROM wawqi_results
        WHERE wqi IS NOT NULL
        LIMIT 2;
    """, "Sample parameters_used JSON structure")
