-- PostGIS initialization script for Schema GIS database
-- This runs automatically when the PostgreSQL container is first created

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Create spatial indexes function for easy use
CREATE OR REPLACE FUNCTION create_spatial_index(table_name text, geom_column text DEFAULT 'geom')
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%s_%s ON %s USING GIST (%s)',
                   table_name, geom_column, table_name, geom_column);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE schema_gis TO schema_user;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'PostGIS extensions installed successfully!';
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
END $$;
