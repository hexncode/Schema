# GIS Layer System

## Auto-Discovery Architecture

The system now **auto-discovers** .gpkg files. No code changes needed to add layers.

## How to Add a New Layer

1. Drop your `.gpkg` file into `atlas/gis/Layers/{category}/`
   - Example: `atlas/gis/Layers/NSW/Roads.gpkg`

2. **(Optional)** Add metadata to `atlas/gis/layers.yaml`:
   ```yaml
   layers:
     Roads:  # Filename without .gpkg
       display_name: "NSW Roads"
       category: "Transport"
       min_zoom: 12
       style:
         color: "#ff0000"
         weight: 2
   ```

3. Restart Django. Done.

## Files

- **layer_manager.py**: New auto-discovery system
  - Scans `Layers/` directory for .gpkg files
  - Loads metadata from layers.yaml (optional)
  - Handles bbox-filtered loading
  - Generates tiles for chunked loading

- **layers.yaml**: Optional metadata (OPTIONAL)
  - Display names, styles, zoom levels
  - If missing, uses sensible defaults

- **service.py**: Needs update (see below)
- **views.py**: Added tile endpoints ✓
- **urls.py**: Added tile routes ✓

## What Still Needs to Be Done

### 1. Install PyYAML

```bash
pip install PyYAML
```

Or add to `requirements.txt`:
```
PyYAML>=6.0
```

### 2. Update service.py

Replace these imports:
```python
# OLD
from atlas.gis.config import catalog, LayerMetadata, LAYERS_PATH
from atlas.gis.nsw_vector_loader import NSWVectorLoader

# NEW
from atlas.gis.config import LAYERS_PATH
from atlas.gis.layer_manager import LayerManager
```

Replace initialization in `GISService.__init__()`:
```python
# OLD
self.catalog = catalog
self.nsw_loader = NSWVectorLoader(LAYERS_PATH)

# NEW
self.layer_manager = LayerManager(LAYERS_PATH)
self.nsw_loader = self.layer_manager  # Backwards compat
```

Update `load_layer()` method:
```python
# Remove hardcoded layer name checks
# OLD:
if layer_name in ['nsw_lots', 'nsw_buildings', 'suburb']:
    gdf = self.nsw_loader.load_layer(layer_name, bbox, zoom_level)

# NEW:
gdf = self.layer_manager.load_layer(layer_name, bbox, zoom_level)
```

### 3. Update Frontend (if needed)

The frontend should work as-is. It calls:
- `/api/gis/tiles/{layer_name}/` - get tile grid
- `/api/gis/tile/{layer_name}/{tile_id}/` - get tile data
- `/api/gis/layer/{layer_name}/` - get full layer (for small layers)

Layer names:
- `Lots.gpkg` → layer_name: `"Lots"`
- `Suburb.gpkg` → layer_name: `"Suburb"`

## API Endpoints

### Tile-Based Loading (for large layers)

```javascript
// 1. Get tiles for viewport
fetch(`/api/gis/tiles/Lots?bbox=${bbox}`)
// Returns: {success: true, tiles: [{id, bbox, bbox_str}, ...]}

// 2. Load each tile
fetch(`/api/gis/tile/Lots/${tile.id}?bbox=${tile.bbox_str}&zoom=${zoom}`)
// Returns: GeoJSON FeatureCollection
```

### Direct Loading (for small layers)

```javascript
fetch(`/api/gis/layer/Suburb?bbox=${bbox}&zoom=${zoom}`)
// Returns: GeoJSON FeatureCollection
```

## Layer Discovery

The system scans `atlas/gis/Layers/` and discovers:

- `Layers/NSW/Lots.gpkg` → `"Lots"` (category: "NSW")
- `Layers/NSW/Suburb.gpkg` → `"Suburb"` (category: "NSW")
- `Layers/Transport/Roads.gpkg` → `"Roads"` (category: "Transport")

No code changes required!

## Default Behavior

Without `layers.yaml`, layers get:
- Display name: Filename with underscores replaced by spaces
- Category: Parent folder name
- Min zoom: 10
- No style overrides
- All attributes included

## Performance

- **Bbox filtering**: Only loads features in viewport
- **Zoom-based simplification**: Reduces vertices at lower zooms
- **Tiling**: Breaks large viewports into chunks
- **Caching**: 15-minute TTL, 100-item LRU cache
- **PyOGrio**: Uses Arrow for 3-5x faster loading (if available)

## Troubleshooting

**"Layer not found"**
- Check filename matches layer_name
- Check .gpkg file is in `Layers/` subdirectory

**"No features loaded"**
- Check bbox is correct (minx, miny, maxx, maxy)
- Check zoom level is >= min_zoom

**Slow loading**
- Ensure bbox is small (use tiling for large areas)
- Check pyogrio is installed: `pip install pyogrio`
- Reduce tile_size in layers.yaml (default: 0.01 degrees)
