# Fixed GIS Vector Layers - Usage Guide

## What Was Fixed

### ✅ Issues Resolved

1. **Layer Not Loading** - Fixed to use actual available layers from catalog
2. **Cadastral/Lot Consolidation** - Cadastral lots now use proper vector data (not Sixmaps WMS)
3. **Zoom Optimization** - Cadastral lots only load at zoom 16+ to handle large datasets
4. **Property Names** - Fixed property name matching for all layer types

## Available Vector Layers

### 🏘️ **Cadastral Lots** (High Detail - Zoom 16+)

These are your **local vector lot boundaries** from the GIS data:

| Layer | Council | Min Zoom | Features |
|-------|---------|----------|----------|
| Inner West Lots | Inner West Council | 16 | Property lots |
| Blacktown Lots | Blacktown City Council | 16 | Property lots |
| Campbelltown Lots | Campbelltown, City of | 16 | Property lots |

**Why Zoom 16+?**
- Each LGA has thousands of lot boundaries
- Loading at lower zoom would be too many features
- Zoom 16+ ensures you're looking at a small area
- Performance remains smooth

**Info Shown:**
- Lot number
- DP (Deposited Plan) number
- Address
- Area (m²)
- LGA name

### 🏛️ **Administrative Layers**

| Layer | Min Zoom | Color | Description |
|-------|----------|-------|-------------|
| **Suburbs** | 11 | Gray dashed | Suburb/locality boundaries |
| **LGA Boundaries** | 8 | Red solid | Local Government Areas |
| **Postcodes** | 10 | Purple | Postcode boundaries |

**Info Shown:**
- **Suburbs**: Suburb name, State
- **LGA**: LGA name, State
- **Postcodes**: Postcode number

### 📊 **Statistical Layers** (ABS)

| Layer | Min Zoom | Color | Description |
|-------|----------|-------|-------------|
| **SA2 Areas** | 11 | Blue dashed | Statistical Area Level 2 |
| **SA3 Areas** | 9 | Green dashed | Statistical Area Level 3 |

**Info Shown:**
- **SA2**: SA2 name, SA3 parent, SA4 region
- **SA3**: SA3 name, SA4 region

### 🗺️ **NSW Sixmaps Layers** (WMS - Legacy)

These are the old WMS layers (raster, not vector):

- **Cadastral WMS** - Shows all NSW lots (raster image)
- **Lot Labels** - Shows lot numbers on map

> **Note**: The new vector cadastral lots are better - they're clickable and show detailed info!

## How to Use

### Step 1: Navigate to Map
```
http://localhost:5000/map
```

### Step 2: Choose Your Layers

#### For Property Analysis
1. Zoom to your area of interest (Sydney, Blacktown, etc.)
2. Zoom in to **level 16 or higher**
3. Toggle on the appropriate **Cadastral Lots** layer
4. Click on any lot to see property details

#### For Market Research
1. Stay at zoom **11-14**
2. Toggle on **Suburbs** and **SA2 Areas**
3. Toggle on **LGA Boundaries** for context
4. Pan around to see different regions

#### For Administrative Context
1. Zoom to **level 8-10**
2. Toggle on **LGA Boundaries**
3. Toggle on **Postcodes**
4. Toggle on **SA3 Areas** for regional stats

### Step 3: Pan and Zoom

- **Pan** the map - layers automatically reload for visible area
- **Zoom in/out** - layers appear/disappear based on zoom level
- **Hover** over features - they highlight
- **Click** on features - popup shows information

## Zoom Level Guide

| Zoom | What You'll See |
|------|-----------------|
| 8-9 | LGA boundaries, SA3 areas |
| 10 | + Postcodes |
| 11-15 | + Suburbs, SA2 areas |
| 16+ | + **Cadastral lots** (property boundaries) |

## Layer Behavior

### Dynamic Loading

All layers load **only the visible area**:
```
User pans → Wait 300ms → Load features in new view → Cache result
```

### Smart Caching

Return to previously viewed area = **instant load** from cache:
```
First view: Loads from API (~500ms)
Return to same view: Loads from cache (~50ms)
```

### Zoom Control

Layers automatically show/hide based on zoom:
```
Zoom < 16: Cadastral lots hidden (too many features)
Zoom >= 16: Cadastral lots visible (manageable number)
```

## Performance Tips

### ✅ Best Practices

1. **Enable only what you need**
   - Don't toggle all layers at once
   - Use administrative layers at low zoom
   - Use cadastral lots only at high zoom

2. **Work at appropriate zoom**
   - Overview: Zoom 8-10 (LGA, Postcodes)
   - Regional: Zoom 11-14 (Suburbs, SA2)
   - Property: Zoom 16+ (Cadastral lots)

3. **Let layers load**
   - Wait a moment after panning
   - Console shows: "Loading layer_name..."
   - Then: "Loaded layer_name: X features"

4. **Use cache effectively**
   - Pan back to areas you've already viewed
   - Instant reload from cache
   - No API call needed

### ⚠️ Performance Issues?

If layers are slow:
1. Disable some layers
2. Zoom out (fewer features)
3. Check browser console for errors
4. Clear cache (refresh page)

## Example Workflows

### Workflow 1: Find Property Details

```
1. Navigate to Inner West area
2. Zoom to level 16 or 17
3. Toggle "Inner West Lots" ON
4. Wait for lots to load (~1-2 seconds)
5. Click on a lot
6. See: Lot number, DP, address, area
```

### Workflow 2: Compare Suburbs

```
1. Navigate to Sydney region
2. Zoom to level 12
3. Toggle "Suburbs" ON
4. Toggle "SA2 Areas" ON
5. Pan around to see different suburbs
6. Click suburbs to see names
```

### Workflow 3: LGA Boundaries

```
1. Zoom to Sydney metro (level 9-10)
2. Toggle "LGA Boundaries" ON
3. Toggle "Postcodes" ON
4. See administrative divisions
5. Click to see LGA names
```

## Troubleshooting

### Layer Doesn't Appear

**Check zoom level:**
```javascript
// Open browser console (F12)
console.log('Current zoom:', map.getZoom());
```

- **LGA**: Need zoom 8+
- **Postcodes**: Need zoom 10+
- **Suburbs/SA2**: Need zoom 11+
- **Cadastral lots**: Need zoom 16+

**Check console for errors:**
```
F12 → Console tab
Look for:
✓ "Loading layer_name..."
✓ "Loaded layer_name: X features"
✗ "Failed to load layer..."
```

### Layer Loads But Wrong Info

**Property names might vary:**
- Some layers use `SAL_NAME21`
- Others use `SAL_NAME_2021`
- Code handles both variants

**Check actual properties:**
```javascript
// In console, after layer loads
console.log(gisLayers.suburbs_2021);
```

### Slow Performance

**Too many features:**
- Zoom out for overview layers
- Zoom in for detail layers
- Don't load cadastral lots at zoom 14 (thousands of features!)

**Disable unneeded layers:**
- Toggle OFF layers you're not using
- Each active layer loads on every pan

## Technical Details

### API Calls

Each layer makes a call like:
```
GET /api/gis/layer/suburbs_2021?bbox=150.9,-33.9,151.3,-33.7&simplify=0.0005
```

Parameters:
- `bbox`: Current view bounds (minx,miny,maxx,maxy)
- `simplify`: Geometry simplification tolerance

### Caching

Cache key format:
```
{layerName}_{zoom}_{west}_{south}_{east}_{north}
```

Example:
```
suburbs_2021_12_150.900_-33.900_151.300_-33.700
```

Cached for instant reload when returning to same view.

### Layer Configurations

Each layer has settings in `map.html`:

```javascript
'cadastral_lots_inner_west_council': {
    style: {
        color: '#2c3e50',      // Dark gray border
        weight: 1.5,           // Border width
        fillOpacity: 0.1       // Light fill
    },
    minZoom: 16,               // Only show at zoom 16+
    simplifyTolerance: 0.00001, // High detail
    isCadastral: true          // Flag for property handling
}
```

## Summary

### What's Working Now

✅ **Cadastral Lots**
- 3 LGA areas with vector lot boundaries
- Load at zoom 16+ for performance
- Clickable with property info

✅ **Administrative Layers**
- Suburbs, LGA, Postcodes
- Appropriate zoom levels
- Full coverage

✅ **Statistical Layers**
- SA2, SA3 areas
- ABS boundaries
- Regional analysis

✅ **Performance**
- Bbox filtering (only visible area)
- Geometry simplification
- Smart caching
- Zoom-based loading

### Quick Reference

| Task | Layers | Zoom |
|------|--------|------|
| Find property details | Cadastral Lots | 16+ |
| Compare suburbs | Suburbs, SA2 | 11-14 |
| See LGA boundaries | LGA, Postcodes | 8-10 |
| Regional analysis | SA2, SA3 | 9-14 |

**Start exploring! Toggle the layers and pan around.** 🗺️
