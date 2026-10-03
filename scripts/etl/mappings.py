# Mapping rules for column aliases to canonical names

# Geography aliases (if any, though most use standard CGWB columns)
GEO_MAPPINGS = {
    'state': 'state',
    'state lgd code': 'state_lgd_code',
    'district': 'district',
    'district lgd code': 'district_lgd_code',
    'tehsil': 'tehsil',
    'block': 'block',
    'village': 'village',
    'station': 'station_name',
    'agency': 'agency',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'data acquisition time': 'sample_date'
}

# The canonical parameters identified in Phase 1
# This maps normalized source header strings (lowercase, stripped) to Canonical ID and Name
PARAMETER_MAPPINGS = {
    'potential of hydrogen (ph)': ('ph', 'Potential of Hydrogen (pH)', 'pH'),
    'electric conductivity (μs/cm)': ('electrical_conductivity', 'Electrical Conductivity', 'μS/cm'),
    'electric conductivity (\u03bcs/cm)': ('electrical_conductivity', 'Electrical Conductivity', 'μS/cm'),
    'total dissolved solids (mg/l)': ('tds', 'Total Dissolved Solids', 'mg/L'),
    'carbonate (mg/l)': ('carbonate', 'Carbonate', 'mg/L'),
    'bicarbonate (mg/l)': ('bicarbonate', 'Bicarbonate', 'mg/L'),
    'total alkalinity (mg/l as caco3)': ('alkalinity', 'Total Alkalinity', 'mg/L'),
    'chloride (mg/l)': ('chloride', 'Chloride', 'mg/L'),
    'nitrate n (mgn/l)': ('nitrate', 'Nitrate N', 'mg/L'),
    'sulphate (mg/l)': ('sulphate', 'Sulphate', 'mg/L'),
    'phosphate(mg/l)': ('phosphate', 'Phosphate', 'mg/L'),
    'silica(mg/l)': ('silica', 'Silica', 'mg/L'),
    'fluoride (mg/l)': ('fluoride', 'Fluoride', 'mg/L'),
    'total hardness (mgcaco3/l)': ('hardness', 'Total Hardness', 'mg/L'),
    'calcium (mg/l)': ('calcium', 'Calcium', 'mg/L'),
    'magnesium (mg/l)': ('magnesium', 'Magnesium', 'mg/L'),
    'sodium (mg/l)': ('sodium', 'Sodium', 'mg/L'),
    'potassium (mg/l)': ('potassium', 'Potassium', 'mg/L'),
    'iron(mg/l)': ('iron', 'Iron', 'mg/L'),
    'arsenic (mg/l)': ('arsenic', 'Arsenic', 'mg/L'),
    'uranium(mg/l)': ('uranium', 'Uranium', 'mg/L'),
    'manganese (mg/l)': ('manganese', 'Manganese', 'mg/L'),
    'copper (mg/l)': ('copper', 'Copper', 'mg/L'),
    'lead (mg/l)': ('lead', 'Lead', 'mg/L'),
    'zinc (mg/l)': ('zinc', 'Zinc', 'mg/L'),
    'nickel (mg/l)': ('nickel', 'Nickel', 'mg/L'),
    'cadmium (mg/l)': ('cadmium', 'Cadmium', 'mg/L'),
    'chromium (mg/l)': ('chromium', 'Chromium', 'mg/L')
}

PLACEHOLDER_VALUES = {'-', 'ND', 'N/A', 'NA', 'NULL', 'BLANK', 'NOT AVAILABLE'}
