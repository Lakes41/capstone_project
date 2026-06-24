
-- Weather Analytics Star Schema

-- Create tables only if they don't exist (instead of dropping)

-- Dimension: Location
CREATE TABLE IF NOT EXISTS dim_location (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    day_of_week INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fact Table: Weather Observations
CREATE TABLE IF NOT EXISTS fact_weather_observations (
    observation_id SERIAL PRIMARY KEY,
    location_id INT REFERENCES dim_location(location_id),
    date_id INT REFERENCES dim_date(date_id),
    temperature_2m_mean NUMERIC(5,2),
    temperature_2m_max NUMERIC(5,2),
    temperature_2m_min NUMERIC(5,2),
    relative_humidity_2m_mean NUMERIC(5,2),
    precipitation_sum NUMERIC(6,2),
    wind_speed_10m_max NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, date_id)
);

-- Staging Table for ELT Workflow
CREATE TABLE IF NOT EXISTS staging_weather_raw (
    staging_id SERIAL PRIMARY KEY,
    raw_data JSONB NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
