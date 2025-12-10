# GIS Restructure Summary

## Overview
The GIS system has been completely restructured to use only NSW-wide GeoPackage layers with optimized loading for large datasets.

## What Changed

### 1. **Removed Old Layers**
All individual LGA-based shapefiles have been removed:
- ❌ Cadastral data from "NSW LGA (Sixmaps)" folder (30+ LGAs)
- ❌ Transport layers (roads, railways)
- ❌ Hydrological layers (water features)
- ❌ Topographic layers (contours)
- ❌ Utility layers (electricity, pipelines)
- ❌ Planning layers (parishes)
- ❌ Statistical areas (ABS data)
- ❌ Administrative boundaries (LGA, suburbs, postcodes)

### 2. **Added NSW-Wide Layers**
Two optimized GeoPackage layers from `app/gis/Layers/NSW/`:
- ✅ **nsw_lots** - NSW_Lots.gpkg (Complete NSW cadastral lot boundaries)
- ✅ **nsw_buildings** - BLD_GreaterSydney.gpkg (Greater Sydney building footprints)

### 3. **File Structure**
All GIS-related code moved to `app/gis/` folder:

```
app/gis/
├── __init__.py           # Package exports
├── config.py             # Layer catalog (simplified, NSW only)
├── service.py            # GIS service (data loading/processing)
├── nsw_vector_loader.py  # Optimized NSW layer loader
└── Layers/
    └── NSW/
        ├── NSW_Lots.gpkg
        └── BLD_GreaterSydney.gpkg
```

**Removed files:**
- ❌ `app/gis_config.py` → moved to `app/gis/config.py`
- ❌ `app/gis_service.py` → moved to `app/gis/service.py`

### 4. **New Features**

#### Zoom-Based Loading
- **NSW Lots**: Only load at zoom level 15+
- **NSW Buildings**: Only load at zoom level 16+

#### Viewport Filtering
- Only loads features within the map bounds (bbox parameter required)
- Prevents loading entire NSW dataset at once

#### Performance Optimizations
- **Feature Limiting**: Max 5000 lots, 3000 buildings per request
- **Auto-Simplification**: Geometries simplified based on zoom level
  - Zoom 15: 0.00005° tolerance
  - Zoom 16: 0.00002° tolerance
  - Zoom 17: 0.00001° tolerance
  - Zoom 18: 0.000005° tolerance
  - Zoom 19+: 0.000001° or no simplification
- **PyOGRIO Engine**: Faster file reading than default Fiona
- **Spatial Filtering**: Reads only viewport features from disk

## API Usage

### Get Catalog
```http
GET /api/gis/catalog
```

**Response:**
```json
{
  "success": true,
  "catalog": {
    "categories": ["NSW"],
    "layers": {
      "nsw_lots": {
        "name": "nsw_lots",
        "display_name": "NSW Property Lots",
        "category": "NSW",
        "subcategory": "Cadastral",
        "min_zoom": 15,
        "exists": true
      },
      "nsw_buildings": {
        "name": "nsw_buildings",
        "display_name": "Greater Sydney Buildings",
        "category": "NSW",
        "subcategory": "Buildings",
        "min_zoom": 16,
        "exists": true
      }
    }
  }
}
```

### Get Layer Data
```http
GET /api/gis/layer/nsw_lots?bbox=151.20,-33.88,151.21,-33.87&zoom=15
```

**Parameters:**
- `bbox` (required): minx,miny,maxx,maxy in EPSG:4326
- `zoom` (optional): Zoom level (default: 15)
- `simplify` (optional): Simplification tolerance

**Response:** GeoJSON FeatureCollection

### Get Layer Info
```http
GET /api/gis/layer/nsw_lots/info
```

### Search Layers
```http
GET /api/gis/search?q=lots
```

### Query Point
```http
POST /api/gis/query/point
Content-Type: application/json

{
  "lat": -33.875,
  "lon": 151.205,
  "layers": ["nsw_lots"]
}
```

## Frontend Integration Example

```javascript
// Initialize map
const map = L.map('map').setView([-33.8688, 151.2093], 13);

// Add base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Layer groups
let lotsLayer = L.layerGroup();
let buildingsLayer = L.layerGroup();

// Load layers on map move
map.on('moveend', function() {
    const zoom = map.getZoom();
    const bounds = map.getBounds();
    const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;

    // Clear existing layers
    lotsLayer.clearLayers();
    buildingsLayer.clearLayers();

    // Load NSW lots (zoom 15+)
    if (zoom >= 15) {
        fetch(`/api/gis/layer/nsw_lots?bbox=${bbox}&zoom=${zoom}`)
            .then(response => response.json())
            .then(data => {
                L.geoJSON(data, {
                    style: {
                        color: '#2c3e50',
                        weight: 1.5,
                        fillOpacity: 0.1
                    }
                }).addTo(lotsLayer);
            });
    }

    // Load buildings (zoom 16+)
    if (zoom >= 16) {
        fetch(`/api/gis/layer/nsw_buildings?bbox=${bbox}&zoom=${zoom}`)
            .then(response => response.json())
            .then(data => {
                L.geoJSON(data, {
                    style: {
                        color: '#34495e',
                        weight: 1,
                        fillColor: '#bdc3c7',
                        fillOpacity: 0.7
                    }
                }).addTo(buildingsLayer);
            });
    }
});

// Add layer controls
L.control.layers(null, {
    'Property Lots': lotsLayer,
    'Buildings': buildingsLayer
}).addTo(map);
```

## Python Usage

```python
from app.gis import gis_service, catalog

# Get all available layers
layers = catalog.get_available_layers()
for layer in layers:
    print(f"{layer.name}: {layer.display_name}")

# Load layer data
bbox = (151.20, -33.88, 151.21, -33.87)  # Sydney CBD
geojson = gis_service.layer_to_geojson('nsw_lots', bbox=bbox, zoom_level=15)

# Query features at a point
features = gis_service.query_features_at_point('nsw_lots', lon=151.205, lat=-33.875)

# Search layers
results = gis_service.search_layers('building')
```

## Testing

Three comprehensive test files have been created:

1. **test_nsw_vectors.py** - Tests NSW vector loader
2. **test_gis_complete.py** - Tests complete GIS structure
3. **test_gis_api.py** - Tests API endpoints

Run tests:
```bash
python test_gis_complete.py
python test_gis_api.py
```

## Performance Benefits

### Before (Old Structure)
- 30+ LGA folders with individual shapefiles
- All features loaded regardless of zoom level
- No viewport filtering
- Slow rendering with many features
- Complex catalog with 100+ layer definitions

### After (New Structure)
- 2 optimized GeoPackage files
- Zoom-based loading (only when zoomed in)
- Viewport filtering (only visible area)
- Auto-simplification (faster rendering)
- Simple catalog with 2 layer definitions
- Feature limiting (max 5000/3000 per request)

**Result:** Significantly faster loading and rendering, especially for large areas like all of NSW.

## Migration Notes

### Import Changes
All code using the old imports needs updating:

**Before:**
```python
from app.gis_config import catalog
from app.gis_service import gis_service
```

**After:**
```python
from app.gis import catalog, gis_service
```

### Updated Files
- `app/routes/main.py` - All GIS endpoints updated
- `app/gis/__init__.py` - Package initialization
- All test files updated

## Summary

✅ **Completed:**
- Removed all old vector layers (LGA shapefiles, statistical areas, admin boundaries)
- Created simplified NSW-only catalog
- Moved all GIS code to `app/gis/` folder
- Implemented optimized NSW vector loader
- Added zoom-based and viewport-based loading
- Updated all imports across application
- Created comprehensive tests
- Verified all API endpoints working

🎯 **Result:**
A clean, performant GIS system focused on NSW property data with optimized loading for large datasets.
