# scripts/wawqi/weights.py
from scripts.wawqi.standards import WAWQI_PARAMETERS

def calculate_weights(active_parameters=None):
    """
    Dynamically calculate K and Wi based on the exact BIS standard methodology.
    
    wi = K / Si
    K = 1 / sum(1/Si)
    """
    if active_parameters is None:
        active_parameters = list(WAWQI_PARAMETERS.keys())
        
    sum_inv_si = 0.0
    for param in active_parameters:
        if param in WAWQI_PARAMETERS:
            limit = WAWQI_PARAMETERS[param]['acceptable_limit']
            sum_inv_si += (1.0 / limit)
            
    K = 1.0 / sum_inv_si if sum_inv_si > 0 else 0.0
    
    weights = {}
    for param in active_parameters:
        if param in WAWQI_PARAMETERS:
            limit = WAWQI_PARAMETERS[param]['acceptable_limit']
            weights[param] = K / limit
            
    return K, weights
