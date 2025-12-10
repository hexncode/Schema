# GIS Layers Quick Start Guide

## Installation

### Step 1: Install GeoPandas Dependencies

**Option A: Using Conda (Recommended for Windows)**
```bash
conda install -c conda-forge geopandas
```

**Option B: Using pip with pre-built wheels (Windows)**
```bash
# Download wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/
# Example for Python 3.11 on Windows 64-bit:

pip install GDAL-3.8.4-cp311-cp311-win_amd64.whl
pip install Fiona-1.9.5-cp311-cp311-win_amd64.whl
pip install geopandas
```

### Step 2: Verify Installation

```bash
python -c "import geopandas; print(f'GeoPandas {geopandas.__version__} installed successfully')"
```

## Testing the GIS System

### Test 1: Check the Catalog

Start your Flask application:
```bash
python run.py
```

Test the catalog endpoint:
```bash
curl http://localhost:5000/api/gis/catalog
```

Or visit in browser:
```
http://localhost:5000/api/gis/catalog
```

### Test 2: Load a Sample Layer

Get information about a layer:
```bash
curl http://localhost:5000/api/gis/layer/lga_2022/info
```

Load the layer (with simplification for faster loading):
```bash
curl "http://localhost:5000/api/gis/layer/lga_2022?simplify=0.001"
```

### Test 3: Query at a Point

Query layers at Sydney coordinates:
```bash
curl -X POST http://localhost:5000/api/gis/query/point \
  -H "Content-Type: application/json" \
  -d '{"lat": -33.8688, "lon": 151.2093, "layers": ["lga_2022", "suburbs_2021"]}'
```

### Test 4: Search for Layers

Search for cadastral layers:
```bash
curl "http://localhost:5000/api/gis/search?q=cadastral"
```

## Using Layers in Your Application

### JavaScript Example (Frontend)

```javascript
// Load the catalog
async function loadCatalog() {
    const response = await fetch('/api/gis/catalog');
    const data = await response.json();
    console.log('Available layers:', data.catalog.layers);
    return data;
}

// Load a specific layer and add to Leaflet map
async function addGISLayer(map, layerName, options = {}) {
    const bounds = map.getBounds();
    const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;

    const url = `/api/gis/layer/${layerName}?bbox=${bbox}&simplify=0.0001`;
    const response = await fetch(url);
    const geojson = await response.json();

    const layer = L.geoJSON(geojson, {
        style: options.style || {
            color: '#3498db',
            weight: 2,
            fillOpacity: 0.2
        },
        onEachFeature: (feature, layer) => {
            if (feature.properties) {
                layer.bindPopup(JSON.stringify(feature.properties, null, 2));
            }
        }
    });

    layer.addTo(map);
    return layer;
}

// Usage
const map = L.map('map').setView([-33.8688, 151.2093], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add LGA boundaries
addGISLayer(map, 'lga_2022', {
    style: { color: '#e74c3c', weight: 2, fillOpacity: 0.1 }
});

// Add suburbs
addGISLayer(map, 'suburbs_2021', {
    style: { color: '#3498db', weight: 1, fillOpacity: 0.05 }
});
```

### Python Example (Backend)

```python
from app.gis_service import gis_service

# Get layer information
info = gis_service.get_layer_info('lga_2022')
print(f"Layer has {info['feature_count']} features")

# Load layer data
gdf = gis_service.load_layer('lga_2022')
print(gdf.head())

# Query at a point
results = gis_service.query_features_at_point('lga_2022', 151.2093, -33.8688)
if results is not None:
    print(f"Found {len(results)} features at point")
    print(results[['LGA_NAME22', 'STE_NAME21']])

# Get all layers at a location
layers_at_point = gis_service.get_layers_for_location(151.2093, -33.8688)
print(f"Available layers: {layers_at_point}")
```

## Common Layer Combinations

### Property Analysis View
```javascript
// Cadastral lots for property boundaries
addGISLayer(map, 'cadastral_lots_inner_west_council');

// Suburbs for context
addGISLayer(map, 'suburbs_2021');

// Buildings
addGISLayer(map, 'buildings_greater_sydney');
```

### Market Analysis View
```javascript
// Statistical areas for demographics
addGISLayer(map, 'sa2_2021');

// LGA boundaries
addGISLayer(map, 'lga_2022');

// Postcodes
addGISLayer(map, 'postcodes_2021');
```

### Infrastructure View
```javascript
// Roads
addGISLayer(map, 'roads_inner_west_council');

// Railways
addGISLayer(map, 'railway_inner_west_council');

// Water features
addGISLayer(map, 'water_features_inner_west_council');
```

## Layer Categories Summary

| Category | Count | Key Layers |
|----------|-------|------------|
| Administrative | 6 | lga_2022, suburbs_2021, postcodes_2021 |
| Statistical Areas | 7 | sa1-sa4_2021, meshblocks_2021 |
| Cadastral | 30+ | Lots, easements per LGA |
| Transport | 12+ | Roads, railways per LGA |
| Hydrology | 6+ | Water features per LGA |
| Buildings | 1 | buildings_greater_sydney |
| Utilities | 6+ | Electricity, pipelines |

## Performance Tips

### 1. Use Bounding Box Filters
Always filter to viewport when loading large layers:
```javascript
const bounds = map.getBounds();
const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
fetch(`/api/gis/layer/buildings_greater_sydney?bbox=${bbox}`)
```

### 2. Simplify Geometries
Use simplification for overview maps:
```javascript
// More simplification (faster, less detail)
fetch('/api/gis/layer/lga_2022?simplify=0.001')

// Less simplification (slower, more detail)
fetch('/api/gis/layer/lga_2022?simplify=0.0001')
```

### 3. Respect Zoom Levels
Only load layers at appropriate zoom levels:
```javascript
map.on('zoomend', function() {
    const zoom = map.getZoom();

    if (zoom >= 15 && !map.hasLayer(cadastralLayer)) {
        // Load detailed cadastral data at high zoom
        addGISLayer(map, 'cadastral_lots_inner_west_council');
    } else if (zoom < 15 && map.hasLayer(cadastralLayer)) {
        // Remove when zoomed out
        map.removeLayer(cadastralLayer);
    }
});
```

### 4. Use Layer Groups
Organize related layers:
```javascript
const infrastructureGroup = L.layerGroup();
addGISLayer(infrastructureGroup, 'roads_inner_west_council');
addGISLayer(infrastructureGroup, 'railway_inner_west_council');
addGISLayer(infrastructureGroup, 'electricity_inner_west_council');

// Add/remove entire group
infrastructureGroup.addTo(map);
```

## Troubleshooting

### "Layer not found" Error
```bash
# Check if layer exists in catalog
curl http://localhost:5000/api/gis/catalog | grep -i "layer_name"

# Check layer info
curl http://localhost:5000/api/gis/layer/layer_name/info
```

### "GDAL not found" Error
```bash
# Verify GDAL installation
python -c "from osgeo import gdal; print(gdal.__version__)"

# Reinstall if needed
conda install -c conda-forge gdal
```

### Layer Loads But Shows in Wrong Location
The system automatically transforms to WGS84. If data appears incorrect:
```python
from app.gis_service import gis_service
gdf = gis_service.load_layer('your_layer')
print(f"CRS: {gdf.crs}")
print(f"Bounds: {gdf.total_bounds}")
```

### Performance Issues
- Use bbox parameter to limit extent
- Increase simplify tolerance
- Check file size and feature count
- Consider using vector tiles for very large datasets

## Next Steps

1. ✅ Install dependencies
2. ✅ Test the API endpoints
3. ✅ Load sample layers
4. 📋 Integrate layers into your map interface
5. 📋 Add layer controls and toggles
6. 📋 Implement layer-specific styling
7. 📋 Add spatial analysis features

## Additional Resources

- **Full Documentation**: See `GIS_LAYERS_README.md`
- **GeoPandas Docs**: https://geopandas.org/
- **Leaflet Docs**: https://leafletjs.com/
- **NSW Planning Portal**: https://www.planningportal.nsw.gov.au/
- **NSW Six Maps**: https://www.six.nsw.gov.au/
