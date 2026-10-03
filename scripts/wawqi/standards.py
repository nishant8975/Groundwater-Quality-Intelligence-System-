# scripts/wawqi/standards.py
# Scientific Configuration for WAWQI

# Standard values (Si) from BIS IS 10500:2012
# Ideal values (Vo) based on pure water definition
# Units must exactly match the database unit column.

WAWQI_PARAMETERS = {
    'ph': {
        'acceptable_limit': 8.5,
        'ideal_value': 7.0,
        'unit': 'pH',
        'source': 'BIS IS 10500:2012'
    },
    'tds': {
        'acceptable_limit': 500.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    },
    'chloride': {
        'acceptable_limit': 250.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    },
    'sulphate': {
        'acceptable_limit': 200.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    },
    'hardness': {
        'acceptable_limit': 200.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    },
    'calcium': {
        'acceptable_limit': 75.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    },
    'magnesium': {
        'acceptable_limit': 30.0,
        'ideal_value': 0.0,
        'unit': 'mg/L',
        'source': 'BIS IS 10500:2012'
    }
}
