import pandas as pd
import numpy as np
from datetime import datetime
from scripts.etl.mappings import PLACEHOLDER_VALUES

def parse_numeric(val):
    if pd.isna(val):
        return None, True, False, "MISSING"
    
    val_str = str(val).strip()
    if val_str == "" or val_str.upper() in PLACEHOLDER_VALUES:
        return None, False, True, "PLACEHOLDER"
        
    try:
        num = float(val_str)
        return num, False, False, "VALID_NUMERIC"
    except ValueError:
        return None, False, False, "INVALID_NUMERIC"

def parse_date(val):
    if pd.isna(val):
        return None, "MISSING"
    
    val_str = str(val).strip()
    if val_str == "":
        return None, "MISSING"
        
    try:
        # Assuming the standard formats like YYYY-MM-DD or DD-MM-YYYY or DD/MM/YYYY
        dt = pd.to_datetime(val_str, errors='coerce')
        if pd.isna(dt):
            return None, "INVALID_DATE"
        return dt.strftime('%Y-%m-%d'), "VALID_DATE"
    except Exception:
        return None, "INVALID_DATE"

def validate_coordinates(lat, lon):
    # India bounding box roughly: Lat 6 to 38, Lon 68 to 98
    lat_valid = False
    lon_valid = False
    
    if lat is not None and 6.0 <= lat <= 38.0:
        lat_valid = True
    if lon is not None and 68.0 <= lon <= 98.0:
        lon_valid = True
        
    if lat is None and lon is None:
        return False, "MISSING"
    if lat_valid and lon_valid:
        return True, "VALID"
    return False, "OUT_OF_RANGE_OR_INVALID"
