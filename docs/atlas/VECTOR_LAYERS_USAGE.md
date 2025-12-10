# Vector Layers - User Guide

## Overview

Your GIS map now includes **dynamic vector layers** that load automatically as you pan and zoom around the map.

## Features

### ✅ Implemented Features

1. **Dynamic Loading** - Layers load only the visible area as you pan
2. **Smart Caching** - Previously viewed areas load instantly from cache
3. **Zoom-Level Control** - Layers only show at appropriate zoom levels
4. **Interactive** - Hover and click features for information
5. **Styled** - Each layer has custom colors and styling
6. **Performance Optimized** - Geometry simplification and bbox filtering

## Available Vector Layers

### 1. **Suburbs** (`suburbs_2021`)
- **Minimum Zoom**: 11
- **Color**: Gray dashed lines
- **Shows**: Suburb/locality boundaries across NSW
- **Info**: Suburb name, state

### 2. **LGA Boundaries** (`lga_2022`)
- **Minimum Zoom**: 8
- **Color**: Red with light red fill
- **Shows**: Local Government Area boundaries
- **Info**: LGA name, state

### 3. **Statistical Areas (SA2)** (`sa2_2021`)
- **Minimum Zoom**: 11
- **Color**: Blue dashed lines
- **Shows**: ABS Statistical Area Level 2 boundaries
- **Info**: SA2 name, SA3 parent region

### 4. **Postcodes** (`postcodes_2021`)
- **Minimum Zoom**: 10
- **Color**: Purple
- **Shows**: Postcode boundaries
- **Info**: Postcode number

### 5. **Buildings** (`buildings_greater_sydney`)
- **Minimum Zoom**: 16 (high zoom only)
- **Color**: Dark gray with light fill
- **Shows**: Building footprints in Greater Sydney
- **Info**: Building attributes

## How to Use

### Basic Usage

1. **Navigate to the map page**: `/map`

2. **Toggle layers**: Use the layer control panel on the left
   - Under "Vector Layers" section
   - Click the switch to turn layers on/off

3. **Pan the map**: Layers automatically reload for the visible area

4. **Zoom in/out**: Layers appear/disappear based on zoom level

### Zoom Level Guide

| Zoom Level | Visible Layers |
|------------|---------------|
| 8-9 | LGA Boundaries |
| 10 | LGA, Postcodes |
| 11-15 | LGA, Postcodes, Suburbs, SA2 |
| 16+ | All layers including Buildings |

### Interacting with Features

**Hover**:
- Move mouse over a feature
- Boundary highlights
- Cursor changes to pointer

**Click**:
- Click on a feature
- Popup shows feature information
- Different info for each layer type

## Performance Tips

### For Best Performance

1. **Enable only needed layers**
   - Don't turn on all layers at once
   - Buildings layer is heavy - use only when zoomed in

2. **Work at appropriate zoom**
   - Zoom in closer for detailed layers
   - Stay zoomed out for overview layers

3. **Let layers finish loading**
   - Wait a moment after panning
   - Layers load after 300ms delay

4. **Use cache effectively**
   - Return to previously viewed areas loads instantly
   - Cache holds last 20 view areas

## Layer Combinations

### Property Analysis
```
✓ Suburbs
✓ LGA Boundaries
✓ Buildings (when zoomed in)
✓ Cadastral Boundaries (NSW Sixmaps)
```

### Market Research
```
✓ Suburbs
✓ Statistical Areas (SA2)
✓ Postcodes
```

### Administrative Context
```
✓ LGA Boundaries
✓ Postcodes
✓ Suburbs
```

## Technical Details

### How It Works

1. **User toggles layer on**
   → JavaScript checks if zoom level is appropriate
   → Fetches GeoJSON for current view bounds

2. **User pans map**
   → 300ms delay (debounce)
   → Checks cache for this view
   → If not cached, fetches new data

3. **Data received**
   → Creates Leaflet GeoJSON layer
   → Applies styling
   → Adds popups and hover effects
   → Caches for future use

### API Endpoints Used

```javascript
/api/gis/layer/{layer_name}?bbox={minx,miny,maxx,maxy}&simplify={tolerance}
```

Example:
```
/api/gis/layer/suburbs_2021?bbox=150.9,-33.9,151.3,-33.7&simplify=0.0005
```

### Styling Configuration

Each layer has a configuration in `map.html`:

```javascript
'suburbs_2021': {
    style: {
        color: '#7f8c8d',           // Border color
        weight: 1.5,                 // Border width
        fillColor: '#ecf0f1',        // Fill color
        fillOpacity: 0.1,            // Fill transparency
        dashArray: '3, 3'            // Dashed line pattern
    },
    minZoom: 11,                     // Minimum zoom to show
    simplifyTolerance: 0.0005        // Geometry simplification
}
```

## Troubleshooting

### Layer Not Showing

**Problem**: Toggled layer but nothing appears

**Solutions**:
1. Check zoom level - zoom in/out to appropriate level
2. Check browser console for errors (F12)
3. Verify API is running: `/api/gis/catalog`
4. Check if data exists for your area

### Slow Loading

**Problem**: Layers take long time to load

**Solutions**:
1. Disable some layers
2. Zoom out to reduce features
3. Buildings layer requires zoom 16+ and loads many features
4. Check network speed

### Features Not Clickable

**Problem**: Can't click on features

**Solutions**:
1. Ensure layer is on top (loaded last)
2. Check if cadastral layer is blocking
3. Try clicking on feature border, not fill

### Wrong Information in Popup

**Problem**: Popup shows incorrect or no data

**Solutions**:
1. This is based on GeoJSON properties
2. Some layers may have different field names
3. Check console for property names
4. Report issue for fixing

## Adding More Layers

To add additional layers from the catalog:

1. **Find layer name** from catalog:
   ```
   Visit: /api/gis/catalog
   ```

2. **Add toggle control** in `map.html`:
   ```html
   <div class="form-check form-switch">
       <input class="form-check-input gis-layer-toggle" type="checkbox"
              id="toggleNewLayer" data-layer="layer_name_here">
       <label class="form-check-label" for="toggleNewLayer">
           Layer Display Name
       </label>
   </div>
   ```

3. **Add configuration** in JavaScript:
   ```javascript
   'layer_name_here': {
       style: {
           color: '#3498db',
           weight: 2,
           fillColor: '#d6eaf8',
           fillOpacity: 0.1
       },
       minZoom: 12,
       simplifyTolerance: 0.001
   }
   ```

4. **Refresh page** and toggle the new layer

## Browser Console Commands

For debugging and testing:

```javascript
// Check loaded layers
console.log(gisLayers);

// Check cache
console.log(gisLayerCache);

// Manually load a layer
loadGISLayer('suburbs_2021');

// Get current bbox
console.log(getViewBbox());

// Force reload all active layers
loadActiveGISLayers();
```

## Future Enhancements

Planned improvements:

- [ ] Layer opacity slider
- [ ] Layer ordering/z-index control
- [ ] Custom styling per user
- [ ] Legend for each layer
- [ ] Filter features by attributes
- [ ] Export visible features
- [ ] Measure tools with layers
- [ ] Print/export map with layers

## Support

### Check Status
1. Open browser console (F12)
2. Look for messages like:
   - `Loading GIS layer: suburbs_2021`
   - `Loaded suburbs_2021: 150 features`
   - `Loading suburbs_2021 from cache`

### Common Messages

**Good**:
- ✓ `Loaded {layer}: {n} features` - Success
- ✓ `Loading {layer} from cache` - Fast cached load

**Warning**:
- ⚠ `No configuration for layer: {name}` - Layer not configured
- ⚠ `Failed to load layer {name}: 404` - Layer file missing

**Error**:
- ✗ `Error loading GIS layer {name}` - Check console for details

## Summary

The vector layer system provides:
- ✅ 5 ready-to-use layers
- ✅ Automatic loading on pan/zoom
- ✅ Smart caching for performance
- ✅ Zoom-level appropriate display
- ✅ Interactive popups and hover
- ✅ Custom styling per layer
- ✅ Performance optimizations

**Just toggle the layers and start exploring!**
