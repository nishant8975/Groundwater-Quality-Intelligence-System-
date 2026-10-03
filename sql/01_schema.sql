-- 01_schema.sql
-- Phase 2 Canonical Data Model

-- 1. SOURCE DATASETS (Provenance)
CREATE TABLE source_datasets (
    dataset_id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    state_inferred VARCHAR(100),
    row_count INTEGER,
    ingestion_batch_id VARCHAR(100),
    ingestion_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. LOCATIONS (Geographic hierarchy)
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    source_dataset_id INTEGER REFERENCES source_datasets(dataset_id),
    state VARCHAR(100),
    state_lgd_code VARCHAR(50),
    district VARCHAR(100),
    district_lgd_code VARCHAR(50),
    tehsil VARCHAR(100),
    block VARCHAR(100),
    village VARCHAR(100),
    station_name VARCHAR(255),
    agency VARCHAR(100),
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    coordinate_validity_flag BOOLEAN
);

-- 3. PARAMETERS (Canonical dictionary)
CREATE TABLE parameters (
    parameter_id SERIAL PRIMARY KEY,
    canonical_name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    default_unit VARCHAR(50),
    description TEXT
);

-- 4. WATER SAMPLES (Observation events)
CREATE TABLE water_samples (
    sample_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    source_dataset_id INTEGER REFERENCES source_datasets(dataset_id),
    source_row_index INTEGER, -- Traceability to raw CSV row
    sample_date DATE,
    raw_date_string VARCHAR(100),
    date_validity_flag BOOLEAN
    -- NOTE: Intentionally not enforcing UNIQUE(location_id, sample_date) 
    -- until deduplication strategy is finalized in later phases.
);

-- 5. SAMPLE PARAMETER VALUES (Measurements)
CREATE TABLE sample_parameter_values (
    sample_id INTEGER REFERENCES water_samples(sample_id) ON DELETE CASCADE,
    parameter_id INTEGER REFERENCES parameters(parameter_id),
    numeric_value NUMERIC(14, 4),
    raw_value_string VARCHAR(255),
    unit VARCHAR(50),
    is_missing BOOLEAN DEFAULT FALSE,
    is_placeholder BOOLEAN DEFAULT FALSE,
    data_quality_flag VARCHAR(50),
    PRIMARY KEY (sample_id, parameter_id)
);

-- ==========================================
-- INDEXES FOR EXPECTED ANALYTICAL PATTERNS
-- ==========================================

-- Fast lookup by geographic levels
CREATE INDEX idx_locations_state ON locations(state);
CREATE INDEX idx_locations_district ON locations(district);

-- Sample lookups
CREATE INDEX idx_samples_location ON water_samples(location_id);
CREATE INDEX idx_samples_date ON water_samples(sample_date);
CREATE INDEX idx_samples_dataset ON water_samples(source_dataset_id);

-- Value lookups by parameter (essential for WAWQI aggregations)
CREATE INDEX idx_values_parameter ON sample_parameter_values(parameter_id);
CREATE INDEX idx_values_numeric ON sample_parameter_values(numeric_value) WHERE numeric_value IS NOT NULL;
