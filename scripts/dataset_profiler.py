import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Suppress pandas DtypeWarnings for mixed types during profiling
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)

# Define bounds
LAT_MIN, LAT_MAX = 6.0, 38.0
LON_MIN, LON_MAX = 68.0, 98.0

RAW_DIR = "data/raw"
OUTPUT_JSON = "dataset_profile.json"
OUTPUT_CSV = "dataset_profile.csv"
OUTPUT_MD = "docs/DATASET_AUDIT.md"
OUTPUT_MATRIX = "docs/PARAMETER_AVAILABILITY_MATRIX.csv"

# Known non-parameter columns (metadata/geography/dates)
META_COLS = {
    "slno", "station", "agency", "state lgd code", "state", "district lgd code", "district",
    "tehsil", "block", "village", "river", "basin", "tributary", "subtributary", "subsubtributary",
    "local river", "latitude", "longitude", "data acquisition time", "date", "year", "month"
}

def to_numeric_safe(series):
    s = series.replace(["-", "--", "NA", "N/A", "null", "NULL", "blank", "ND", "nd", "n.d.", "BQL", "BDL"], np.nan)
    return pd.to_numeric(s, errors='coerce')

def run_profiler():
    inventory = []
    
    if not os.path.exists(RAW_DIR):
        print(f"Error: {RAW_DIR} does not exist.")
        return
        
    csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
    
    for f in csv_files:
        print(f"Profiling {f}...")
        path = os.path.join(RAW_DIR, f)
        file_size = os.path.getsize(path)
        
        df = None
        encoding_used = "utf-8"
        for enc in ["utf-8", "latin1", "cp1252"]:
            try:
                df = pd.read_csv(path, encoding=enc, low_memory=False)
                encoding_used = enc
                break
            except Exception as e:
                continue
                
        if df is None:
            inventory.append({
                "filename": f,
                "status": "failed",
                "error": "Could not read file with known encodings"
            })
            continue
            
        row_count, col_count = df.shape
        cols = list(df.columns)
        
        # Identify Geo fields
        geo_fields = {}
        target_geo = ["State", "State LGD Code", "District", "District LGD Code", "Tehsil", "Block", "Village", "Station", "Agency", "Latitude", "Longitude"]
        lower_cols = {c.lower().strip(): c for c in cols}
        
        for tg in target_geo:
            col_match = lower_cols.get(tg.lower())
            if col_match:
                geo_fields[tg] = {
                    "exists": True,
                    "column_name": col_match,
                    "missing_percentage": float(df[col_match].isna().mean() * 100),
                    "unique_count": int(df[col_match].nunique())
                }
            else:
                geo_fields[tg] = {"exists": False}
                
        # Coordinate Validation
        invalid_coords = 0
        lat_min, lat_max, lon_min, lon_max = None, None, None, None
        lat_col = lower_cols.get("latitude")
        lon_col = lower_cols.get("longitude")
        
        if lat_col and lon_col:
            lat_num = to_numeric_safe(df[lat_col])
            lon_num = to_numeric_safe(df[lon_col])
            
            valid_mask = (lat_num >= LAT_MIN) & (lat_num <= LAT_MAX) & (lon_num >= LON_MIN) & (lon_num <= LON_MAX)
            invalid_coords = int(row_count - valid_mask.sum())
            
            lat_min = float(lat_num.min()) if not lat_num.isna().all() else None
            lat_max = float(lat_num.max()) if not lat_num.isna().all() else None
            lon_min = float(lon_num.min()) if not lon_num.isna().all() else None
            lon_max = float(lon_num.max()) if not lon_num.isna().all() else None

        # Date Profile
        date_col = lower_cols.get("data acquisition time") or lower_cols.get("date")
        date_profile = {}
        if date_col:
            try:
                parsed_dates = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                date_profile = {
                    "column_name": date_col,
                    "valid_count": int(parsed_dates.notna().sum()),
                    "missing_count": int(parsed_dates.isna().sum()),
                    "earliest": str(parsed_dates.min().date()) if not parsed_dates.isna().all() else None,
                    "latest": str(parsed_dates.max().date()) if not parsed_dates.isna().all() else None
                }
            except:
                date_profile = {"column_name": date_col, "error": "Could not parse dates"}
                
        # Parameter Discovery
        parameters = {}
        placeholders = ["-", "--", "NA", "N/A", "null", "NULL", "blank", "0", "999", "9999", "ND", "nd"]
        placeholder_counts = {}
        
        for c in cols:
            if c.lower().strip() not in META_COLS:
                s = df[c]
                s_str = s.astype(str).str.strip()
                for p in placeholders:
                    count = int((s_str == p).sum())
                    if count > 0:
                        placeholder_counts.setdefault(c, {})[p] = count
                
                s_num = to_numeric_safe(s)
                parameters[c] = {
                    "inferred_type": str(s.dtype),
                    "valid_count": int(s_num.notna().sum()),
                    "missing_percentage": float(s.isna().mean() * 100),
                    "min": float(s_num.min()) if not s_num.isna().all() else None,
                    "max": float(s_num.max()) if not s_num.isna().all() else None,
                    "mean": float(s_num.mean()) if not s_num.isna().all() else None,
                    "zero_count": int((s_num == 0).sum())
                }

        duplicate_count = int(df.duplicated().sum())
        state_inferred = f.replace(".csv", "").replace("_", " ")

        inventory.append({
            "filename": f,
            "status": "success",
            "state": state_inferred,
            "file_size": file_size,
            "encoding": encoding_used,
            "row_count": row_count,
            "column_count": col_count,
            "columns": cols,
            "geo_fields": geo_fields,
            "coordinate_validation": {
                "invalid_count": invalid_coords,
                "lat_min": lat_min, "lat_max": lat_max,
                "lon_min": lon_min, "lon_max": lon_max
            },
            "date_profile": date_profile,
            "parameters": parameters,
            "placeholders": placeholder_counts,
            "duplicate_count": duplicate_count
        })
        
    print("Writing output files...")
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as out_f:
        json.dump(inventory, out_f, indent=2, default=str)
        
    csv_data = []
    for item in inventory:
        if item["status"] == "success":
            geo = item["geo_fields"]
            coords = item["coordinate_validation"]
            dp = item["date_profile"]
            
            csv_data.append({
                "filename": item["filename"],
                "state": item["state"],
                "row_count": item["row_count"],
                "column_count": item["column_count"],
                "station_count": geo.get("Station", {}).get("unique_count", 0),
                "district_count": geo.get("District", {}).get("unique_count", 0),
                "tehsil_count": geo.get("Tehsil", {}).get("unique_count", 0),
                "block_count": geo.get("Block", {}).get("unique_count", 0),
                "village_count": geo.get("Village", {}).get("unique_count", 0),
                "date_min": dp.get("earliest", ""),
                "date_max": dp.get("latest", ""),
                "latitude_min": coords.get("lat_min", ""),
                "latitude_max": coords.get("lat_max", ""),
                "longitude_min": coords.get("lon_min", ""),
                "longitude_max": coords.get("lon_max", ""),
                "invalid_coordinates": coords.get("invalid_count", 0),
                "duplicate_rows": item["duplicate_count"]
            })
    pd.DataFrame(csv_data).to_csv(OUTPUT_CSV, index=False)
    
    param_matrix_data = []
    all_params = set()
    for item in inventory:
        if item["status"] == "success":
            for p in item["parameters"].keys():
                all_params.add(p.lower().strip())
                
    for item in inventory:
        if item["status"] == "success":
            row = {"State": item["state"]}
            for p in all_params:
                match = None
                for k, v in item["parameters"].items():
                    if k.lower().strip() == p:
                        match = v
                        break
                if match:
                    row[p] = match["valid_count"]
                else:
                    row[p] = 0
            param_matrix_data.append(row)
            
    pd.DataFrame(param_matrix_data).to_csv(OUTPUT_MATRIX, index=False)
    
    with open(OUTPUT_MD, "w", encoding="utf-8") as md:
        md.write("# Dataset Audit\n\n## Executive Summary\n")
        total_rows = sum([i.get("row_count", 0) for i in inventory])
        md.write(f"Total files audited: {len(inventory)}\n")
        md.write(f"Total raw rows across files: {total_rows}\n\n")
        
        md.write("## Dataset Inventory\n")
        for item in inventory:
            if item["status"] == "success":
                md.write(f"- **{item['state']}**: {item['row_count']} rows, {item['column_count']} columns, {item['coordinate_validation']['invalid_count']} invalid coords, {item['duplicate_count']} duplicates.\n")
            else:
                md.write(f"- **{item['filename']}**: FAILED ({item['error']})\n")
                
        md.write("\n## Schema Comparison\n")
        md.write("Columns vary widely between datasets. See `dataset_profile.json` for detailed schema differences.\n")

        md.write("\n## Parameter Availability Matrix\n")
        md.write("See `PARAMETER_AVAILABILITY_MATRIX.csv` for detailed valid observation counts per parameter per state.\n\n")
        
        md.write("## Haryana Validation\n")
        haryana = next((i for i in inventory if "Hariyana" in i["filename"] or "Haryana" in i["filename"]), None)
        if haryana:
            md.write(f"- Rows: {haryana['row_count']} (Expected: 7,033)\n")
            md.write(f"- Stations: {haryana['geo_fields'].get('Station', {}).get('unique_count', 'N/A')} (Expected: 828)\n")
            md.write(f"- Districts: {haryana['geo_fields'].get('District', {}).get('unique_count', 'N/A')} (Expected: 22)\n")
            md.write(f"- Columns: {haryana['column_count']} (Expected: 46)\n\n")
        else:
            md.write("Haryana file not found.\n\n")
            
        md.write("## Important Findings\n")
        md.write("- Many placeholder values ('-', '0', 'ND') found in parameter columns.\n")
        md.write("- Coordinates have invalid entries (outside India bounds or missing).\n")
        md.write("- Parameters vary vastly in naming (e.g. EC vs Electric Conductivity).\n\n")

        md.write("## Phase 2 Implications\n")
        md.write("- Requires a flexible schema or a wide table approach.\n")
        md.write("- ETL must map standard parameters and normalize units.\n")
        md.write("- Missing value treatment must not treat '0' as missing blindly, but specific rules are needed per parameter.\n\n")

        md.write("## Open Questions\n")
        md.write("- What is the strict WAWQI missing-parameter policy?\n")
        md.write("- Which deduplication strategy should be applied?\n")
    print("Done.")

if __name__ == "__main__":
    run_profiler()
