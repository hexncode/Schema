# GIS Layers Documentation

This document describes the GIS layer infrastructure for the NSW Property Appraisal application.

## Overview

The application now includes comprehensive GIS layer support with **organized, categorized, and validated** data layers covering:

- Administrative boundaries
- Statistical areas (ABS)
- Cadastral data (property lots)
- Transport infrastructure
- Hydrological features
- Topographic data
- Building footprints
- Utilities infrastructure
- Planning zones

## Architecture

### Components

1. **gis_config.py** - Layer catalog and metadata management
   - Defines all available GIS layers
   - Organizes layers by category and subcategory
   - Stores display properties and styling information

2. **gis_service.py** - GIS data loading and processing
   - Loads vector data from various formats (Shapefile, GeoPackage, GeoJSON)
   - Converts to GeoJSON for web display
   - Supports spatial queries and filtering
   - Handles coordinate system transformations

3. **API Endpoints** (in routes/main.py)
   - `/api/gis/catalog` - Get complete layer catalog
   - `/api/gis/layer/<name>` - Load layer data as GeoJSON
   - `/api/gis/layer/<name>/info` - Get layer information
   - `/api/gis/query/point` - Query layers at a point
   - `/api/gis/search` - Search for layers

## Layer Categories

### 1. Administrative Boundaries

| Layer | File Format | Description |
|-------|-------------|-------------|
| lga_2022 | GeoPackage | Local Government Areas (2022) |
| lga_2021 | GeoPackage | Local Government Areas (2021) |
| sed_2022 | GeoPackage | State Electoral Districts (2022) |
| ced_2021 | GeoPackage | Federal Electoral Divisions (2021) |
| suburbs_2021 | GeoPackage | Suburbs & Localities (SAL) |
| postcodes_2021 | GeoPackage | Postal Areas (POA) |

### 2. Statistical Areas (ABS)

Australian Bureau of Statistics hierarchical statistical areas:

| Layer | Level | Description |
|-------|-------|-------------|
| gccsa_2021 | National | Greater Capital City Statistical Areas |
| sa4_2021 | State | Statistical Area Level 4 (largest sub-state) |
| sa3_2021 | Regional | Statistical Area Level 3 |
| sa2_2021 | Regional | Statistical Area Level 2 (most commonly used) |
| sa1_2021 | Local | Statistical Area Level 1 (smallest) |
| meshblocks_2021 | Census | Mesh Blocks (smallest geographic unit) |

### 3. Cadastral Data (NSW Sixmaps)

Property lot boundaries and related cadastral information for major LGAs:

- Inner West Council
- Blacktown City Council
- Cumberland City Council
- Campbelltown, City of
- Hornsby Shire
- Fairfield, City of

Each LGA includes:
- **Lot boundaries** - Property parcel boundaries
- **Easements** - Property easements and restrictions
- **Roads** - Road centerlines and polygons
- **Railways** - Rail infrastructure
- **Parishes** - Historical cadastral divisions

### 4. Transport Infrastructure

- Road networks
- Railway lines
- Road corridors
- Railway corridors

### 5. Hydrological Features

- Water bodies
- Water features
- Water feature corridors
- Hydro lines and areas

### 6. Topographic Features

- Contour lines
- Spot heights
- Relative heights

### 7. Buildings

- **buildings_greater_sydney** - Building footprints for Greater Sydney (GeoPackage)

### 8. Utilities

- Electricity transmission lines
- Pipelines (water/gas)
- Utility water supply canals

## Data Formats

The system supports multiple GIS formats:

- **Shapefile (.shp)** - ESRI Shapefile format (most cadastral data)
- **GeoPackage (.gpkg)** - Modern vector format (statistical areas, administrative boundaries)
- **GeoJSON (.geojson)** - Web-friendly JSON format (output format)

All data is automatically converted to WGS84 (EPSG:4326) for web mapping compatibility.

## API Usage Examples

### Get the complete catalog

```bash
GET /api/gis/catalog
```

Response:
```json
{
  "success": true,
  "catalog": {
    "categories": ["Administrative", "Statistical Areas", "Cadastral", ...],
    "layers": {
      "lga_2022": {
        "name": "lga_2022",
        "display_name": "NSW Local Government Areas (2022)",
        "category": "Administrative",
        "subcategory": "Local Government",
        "description": "Local Government Area boundaries for NSW",
        "exists": true
      },
      ...
    }
  },
  "summary": {
    "total_layers": 150,
    "available_layers": 145,
    "categories": {...}
  }
}
```

### Load a layer as GeoJSON

```bash
GET /api/gis/layer/lga_2022
```

Optional parameters:
- `bbox` - Bounding box filter: `minx,miny,maxx,maxy`
- `simplify` - Simplification tolerance (degrees)

Example with bbox:
```bash
GET /api/gis/layer/suburbs_2021?bbox=150.9,-33.9,151.3,-33.7&simplify=0.0001
```

### Get layer information

```bash
GET /api/gis/layer/buildings_greater_sydney/info
```

Response:
```json
{
  "success": true,
  "layer": {
    "name": "buildings_greater_sydney",
    "display_name": "Building Footprints - Greater Sydney",
    "category": "Buildings",
    "format": "gpkg",
    "exists": true,
    "feature_count": 1234567,
    "bounds": {
      "minx": 150.5,
      "miny": -34.0,
      "maxx": 151.5,
      "maxy": -33.5
    },
    "attributes": ["OBJECTID", "feature_type", "height", ...]
  }
}
```

### Query layers at a point

```bash
POST /api/gis/query/point
Content-Type: application/json

{
  "lat": -33.8688,
  "lon": 151.2093,
  "layers": ["lga_2022", "suburbs_2021", "sa2_2021"]
}
```

Response includes all features that intersect the point.

### Search for layers

```bash
GET /api/gis/search?q=suburb
```

Returns all layers matching "suburb" in name, display name, or description.

## Frontend Integration

The layers can be easily added to the Leaflet map in `map.html`:

```javascript
// Load a layer from the API
async function loadGISLayer(layerName) {
    const response = await fetch(`/api/gis/layer/${layerName}?simplify=0.0001`);
    const geojson = await response.json();

    // Add to map
    L.geoJSON(geojson, {
        style: {
            color: '#3498db',
            weight: 2,
            fillOpacity: 0.3
        }
    }).addTo(map);
}

// Load suburbs layer
loadGISLayer('suburbs_2021');
```

## Layer Selection by Use Case

### Property Valuation Analysis
- `cadastral_lots_*` - Property boundaries
- `suburbs_2021` - Suburb context
- `lga_2022` - Council boundaries
- `buildings_greater_sydney` - Building footprints
- `sa2_2021` - Statistical comparables

### Transport Accessibility
- `roads_*` - Road networks
- `railway_*` - Rail lines
- `tz_nsw_2016` - Travel zones

### Market Analysis
- `sa2_2021` - Standard reporting regions
- `postcodes_2021` - Postal areas
- `suburbs_2021` - Suburb markets

### Environmental Assessment
- `water_features_*` - Water bodies
- `contours_*` - Topography
- `bushfire` layers via NSW Planning Portal (WMS)

## Performance Optimization

The system includes several optimizations:

1. **Bounding box filtering** - Only load features in view
2. **Geometry simplification** - Reduce complexity for web display
3. **Coordinate transformation** - Automatic conversion to web Mercator
4. **Format support** - Efficient formats (GeoPackage) for large datasets

### Recommended Zoom Levels

- **8-10**: LGA, Electoral districts, SA4
- **11-13**: Suburbs, Postcodes, SA2, SA3
- **14-15**: Roads, SA1, Cadastral lots
- **16+**: Buildings, Contours, Detailed features

## Installation

### Prerequisites

The GIS functionality requires GeoPandas and its dependencies:

```bash
# Install GDAL first (Windows - use pre-built wheels)
pip install GDAL-3.x.x-cpXX-cpXX-win_amd64.whl

# Install Fiona
pip install Fiona-1.x.x-cpXX-cpXX-win_amd64.whl

# Install GIS requirements
pip install -r requirements_gis.txt
```

**Alternative (Recommended for Windows):**
```bash
conda install -c conda-forge geopandas
```

## Data Sources

- **NSW Cadastral Data**: NSW Six Maps (Sixmaps)
- **Administrative Boundaries**: ABS, NSW Planning
- **Statistical Areas**: Australian Bureau of Statistics (ASGS 2021)
- **Building Footprints**: Geoscape Australia
- **Transport Zones**: Transport for NSW (TfNSW)

## Future Enhancements

Planned improvements:

1. **Vector tiles** - More efficient delivery for large datasets
2. **Caching** - Server-side caching of commonly requested areas
3. **Additional LGAs** - Expand cadastral coverage
4. **Live planning data** - Real-time integration with NSW Planning Portal
5. **3D buildings** - Height information and 3D visualization
6. **Property analytics** - Automated spatial analysis tools

## Troubleshooting

### Layer not loading
- Check if file exists: Call `/api/gis/layer/<name>/info`
- Verify GDAL installation: `python -c "import geopandas; print(geopandas.__version__)"`
- Check file permissions on GIS data directory

### Slow performance
- Use bounding box parameter to limit extent
- Apply geometry simplification for overview maps
- Use appropriate zoom levels (don't load detailed data at low zoom)

### Coordinate system issues
- All data is automatically transformed to WGS84 (EPSG:4326)
- Check source CRS if data appears in wrong location

## Support

For issues or questions:
1. Check layer exists in catalog: `/api/gis/catalog`
2. Review layer info: `/api/gis/layer/<name>/info`
3. Check server logs for detailed error messages
