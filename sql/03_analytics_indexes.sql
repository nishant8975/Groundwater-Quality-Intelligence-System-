
-- 03_analytics_indexes.sql

-- WAWQI results performance
CREATE INDEX IF NOT EXISTS idx_wawqi_results_wqi ON wawqi_results(wqi);
CREATE INDEX IF NOT EXISTS idx_wawqi_results_status ON wawqi_results(calculation_status);

-- Location hierarchy performance
CREATE INDEX IF NOT EXISTS idx_locations_state_district ON locations(state, district);
CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- Water samples performance
CREATE INDEX IF NOT EXISTS idx_water_samples_location ON water_samples(location_id);
CREATE INDEX IF NOT EXISTS idx_water_samples_date ON water_samples(sample_date);

-- Sample parameter values performance
CREATE INDEX IF NOT EXISTS idx_spv_parameter_numeric ON sample_parameter_values(parameter_id, numeric_value);
