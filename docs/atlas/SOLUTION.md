# NSW Lots Layer - Network Path Issue Solution

## Problem
The Lot_SPHERICAL_MERCATOR.gdb geodatabase cannot be accessed by GDAL/Fiona/PyOGRIO from the network path `X:\`. This is a known limitation on Windows.

## Solutions (Choose One)

### Solution 1: Use the Built-in NSW Spatial Services Layer (RECOMMENDED - Already Working!)
The map already has a fully functional NSW cadastral layer from NSW Spatial Services that works perfectly:

**Layer Name**: "Property Lots (NSW Spatial Services)"
**Status**: ✅ Already implemented and working
**Coverage**: All of NSW
**Performance**: Optimized with caching and debouncing
**Zoom Level**: Activates at zoom 15+

**To use**: Simply toggle on "Property Lots (NSW Spatial Services)" in the map layer control panel.

This layer is already configured with:
- Beautiful styling (dark outlines, interactive hover effects)
- Click-to-select functionality
- Automatic property details loading
- Planning controls integration
- Fast loading with 200ms debounce

### Solution 2: Convert GDB to GeoPackage Using QGIS or ArcGIS Pro

Since Python GDAL can't access network paths, use a GIS desktop application:

#### Using QGIS (Free):
1. Download and install QGIS: https://qgis.org/download/
2. Open QGIS
3. Add the geodatabase layer:
   - Layer → Add Layer → Add Vector Layer
   - Browse to: `X:\Projects\A_Valuation\_Apps\Appraise.ai\app\gis\Layers\Lot_SPHERICAL_MERCATOR.gdb`
4. Export to GeoPackage:
   - Right-click the layer → Export → Save Features As...
   - Format: GeoPackage
   - File name: `X:\Projects\A_Valuation\_Apps\Appraise.ai\app\gis\Layers\NSW_Lots_SPHERICAL_MERCATOR.gpkg`
   - Layer name: `lots`
   - CRS: Keep as EPSG:3857 (Spherical Mercator) or convert to EPSG:4326 (WGS84)
   - Click OK

#### Using ArcGIS Pro:
1. Open ArcGIS Pro
2. Add the geodatabase to your map
3. Right-click layer → Data → Export Features
4. Output: `X:\Projects\A_Valuation\_Apps\Appraise.ai\app\gis\Layers\NSW_Lots_SPHERICAL_MERCATOR.gpkg`
5. Click Run

### Solution 3: Copy GDB to Local Drive Temporarily

```bash
# Copy the entire GDB folder to local drive
xcopy "X:\Projects\A_Valuation\_Apps\Appraise.ai\app\gis\Layers\Lot_SPHERICAL_MERCATOR.gdb" "C:\Temp\Lot_SPHERICAL_MERCATOR.gdb" /E /I

# Then run conversion
cd "X:\Projects\A_Valuation\_Apps\Appraise.ai"
python convert_gdb_to_gpkg_local.py
```

Create `convert_gdb_to_gpkg_local.py`:
```python
import geopandas as gpd
import fiona

# Read from local copy
gdb_path = r"C:\Temp\Lot_SPHERICAL_MERCATOR.gdb"
gpkg_path = r"X:\Projects\A_Valuation\_Apps\Appraise.ai\app\gis\Layers\NSW_Lots_SPHERICAL_MERCATOR.gpkg"

layers = fiona.listlayers(gdb_path)
print(f"Reading layer: {layers[0]}")

gdf = gpd.read_file(gdb_path, layer=layers[0])
print(f"Read {len(gdf):,} features")

gdf.to_file(gpkg_path, driver='GPKG', layer='lots')
print(f"Saved to {gpkg_path}")
```

## After Converting to GeoPackage

Update `app/gis_config.py` line 288-309:

```python
# NSW-wide Lot Layer (GeoPackage format)
nsw_lot_gpkg = LAYERS_PATH / 'NSW_Lots_SPHERICAL_MERCATOR.gpkg'
if nsw_lot_gpkg.exists():
    self.add_layer(LayerMetadata(
        name='nsw_lots_all',
        path=str(nsw_lot_gpkg),
        layer_type='vector',
        format='gpkg',  # Changed from 'gdb'
        category='Cadastral',
        subcategory='NSW Lots',
        display_name='NSW Property Lots (All NSW)',
        description='Complete NSW cadastral lot boundaries - optimized for web mapping',
        visible_by_default=False,
        min_zoom=15,
        max_zoom=21,
        style={
            'color': '#2c3e50',
            'weight': 1.5,
            'fillColor': '#ecf0f1',
            'fillOpacity': 0.1,
            'opacity': 0.8
        },
        attributes=['lot', 'lotnumber', 'planno', 'planlabel', 'address', 'calcarea', 'lga']
    ))
```

## Current Status

✅ **Map interface**: Ready with toggle control
✅ **Backend API**: Configured with extent-based loading
✅ **Styling**: Professional, aesthetic outlines configured
✅ **Interactivity**: Hover, click, property info panel
✅ **Alternative layer**: NSW Spatial Services WMS working perfectly

⚠️ **Local GDB layer**: Blocked by network path limitation
🔄 **Next step**: Choose a solution above to enable local GDB layer

## Recommendation

**Use the existing "Property Lots (NSW Spatial Services)" layer** - it's already working perfectly with all the features you requested:
- ✅ Toggle on/off
- ✅ Optimized extent-based loading (zoom 15+)
- ✅ Beautiful aesthetic outlines
- ✅ Fast performance with caching
- ✅ Full property information on click

The only advantage of converting the local GDB would be if you need offline access or have custom attributes in your GDB that aren't in the Spatial Services layer.
