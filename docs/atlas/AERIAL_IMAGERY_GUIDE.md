# NSW Aerial Imagery - Usage Guide

## Overview

Your GIS map now includes **high-resolution aerial imagery** from NSW Spatial Services (SixMaps) with three base map options.

## Base Map Options

### 1. **Street Map** (Default)
- Traditional street map from OpenStreetMap
- Shows roads, labels, landmarks
- Good for navigation and context
- Default view on map load

### 2. **Aerial Imagery** ⭐
- High-resolution aerial photography
- NSW Spatial Services imagery
- Recent aerial photos of NSW
- Excellent for property analysis
- No street labels (clean view)

### 3. **Hybrid** ⭐⭐
- Aerial imagery with street labels
- Best of both worlds
- Great for property identification
- Aerial photos + road names + labels

## How to Use

### Switch Base Maps

1. **Find the Layer Control Panel** (left side of map)
2. **Locate "Base Map" section** (at the top)
3. **Select your preferred view:**
   - ⚪ Street Map (default)
   - ⚪ Aerial Imagery
   - ⚪ Hybrid (Aerial + Labels)

### Quick Switch

```
Click any radio button to instantly switch base maps:
Street Map → Aerial Imagery → Hybrid
```

The map instantly switches - no reload needed!

## When to Use Each

### Street Map
**Best for:**
- Finding addresses
- Navigation
- Understanding street layout
- General orientation
- Low-bandwidth situations

**Use when:**
- You need street names
- Finding a location
- Understanding access routes

### Aerial Imagery
**Best for:**
- Property analysis
- Land features
- Building footprints
- Vegetation assessment
- Site context
- Clean unobstructed view

**Use when:**
- Analyzing property features
- Measuring buildings
- Assessing site conditions
- Viewing land use
- Checking vegetation/trees

### Hybrid
**Best for:**
- Property identification
- Combining aerial + context
- Finding specific properties
- Detailed analysis with labels

**Use when:**
- You need both aerial AND labels
- Finding specific address on aerial
- Property research
- Client presentations

## Integration with Other Layers

### Aerial + Cadastral Lots

```
1. Select: Aerial Imagery or Hybrid
2. Zoom to: 15+
3. Toggle: Property Lots (All LGAs) ON
4. Result: See aerial photos with lot boundaries
```

**Perfect for:**
- Property boundaries on aerial
- Lot identification
- Site analysis

### Aerial + Planning Layers

```
1. Select: Aerial Imagery
2. Toggle: Zoning ON
3. Result: See zoning colors overlaid on aerial
```

**Perfect for:**
- Zoning analysis
- Land use assessment
- Planning context

### Aerial + Administrative Layers

```
1. Select: Hybrid (labels helpful)
2. Toggle: Suburbs ON
3. Toggle: LGA Boundaries ON
4. Result: Aerial + suburb boundaries + labels
```

**Perfect for:**
- Regional context
- Market analysis
- Understanding locality

## Layer Stacking

When using aerial imagery, layers stack as:

```
Top → Bottom:
1. Vector overlays (Lots, Suburbs, etc.)
2. Planning layers (Zoning, Heritage, etc.)
3. Labels (if Hybrid selected)
4. Aerial imagery (base)
```

All vector layers work perfectly over aerial imagery!

## Image Quality

### NSW Spatial Services Imagery

- **Source**: NSW SixMaps
- **Coverage**: All of NSW
- **Resolution**: High-resolution aerial photography
- **Max Zoom**: Level 21 (very detailed)
- **Updates**: Regularly updated by NSW government

### Zoom Levels

| Zoom | Detail Level | Use Case |
|------|--------------|----------|
| 6-10 | Regional view | Overview, regional context |
| 11-14 | Suburb level | Local area, multiple properties |
| 15-17 | Property level | Individual lots, buildings |
| 18-21 | High detail | Building features, landscaping |

## Performance

### Loading Speed

- **First load**: 1-3 seconds (downloading tiles)
- **Cached tiles**: Instant (browser cache)
- **Switching bases**: Instant (just changes layer)

### Tips for Best Performance

1. **Let tiles load** - Wait a moment after panning
2. **Use appropriate zoom** - Don't zoom out too far on aerial
3. **Cache works** - Return to previously viewed areas = instant load
4. **Hybrid uses more bandwidth** - Two layers (aerial + labels)

## Use Cases

### Property Valuation

```
Workflow:
1. Hybrid base map
2. Zoom to property (level 17-18)
3. Toggle cadastral lots ON
4. Click lot for details
5. Analyze:
   - Building size from aerial
   - Lot boundaries from cadastral
   - Surrounding context from imagery
   - Property details from popup
```

### Site Analysis

```
Workflow:
1. Aerial Imagery base
2. Zoom to site (level 16-18)
3. Assess:
   - Existing buildings
   - Vegetation/trees
   - Access points
   - Neighboring properties
   - Topography (from shadows)
4. Toggle planning layers for constraints
```

### Market Research

```
Workflow:
1. Hybrid base
2. Zoom to suburb (level 13-15)
3. Toggle Suburbs + SA2 ON
4. Pan around viewing:
   - Urban density from aerial
   - Property types
   - Land use patterns
5. Click suburbs for stats
```

### Client Presentations

```
Best settings:
- Base: Hybrid (clear + informative)
- Zoom: 16-17 (good detail)
- Layers: Cadastral lots + relevant planning
- Result: Professional, clear, informative
```

## Keyboard Shortcuts

While no built-in shortcuts exist, you can:

```javascript
// Add to browser console for quick switching
function switchToAerial() {
    document.getElementById('baseAerial').click();
}

function switchToHybrid() {
    document.getElementById('baseHybrid').click();
}

function switchToStreet() {
    document.getElementById('baseOSM').click();
}

// Usage: Type switchToAerial() in console
```

## Troubleshooting

### Aerial Imagery Not Loading

**Check 1: Internet Connection**
```
Aerial tiles are larger than street map tiles
Requires stable internet connection
```

**Check 2: Zoom Level**
```
Imagery available from zoom 6-21
If too zoomed out, may not load
```

**Check 3: Location**
```
Imagery covers NSW only
Outside NSW may not have imagery
```

### Blurry or Low Quality

**Solution: Zoom in**
```
Aerial imagery improves with zoom level
Zoom to 16+ for best quality
Zoom 18-21 for maximum detail
```

### Tiles Not Updating

**Solution: Refresh**
```
Hard refresh browser: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
Clears tile cache
Forces reload
```

### Labels Hard to Read on Aerial

**Solution: Use Hybrid Mode**
```
Switch from Aerial to Hybrid
Labels have better contrast
Semi-transparent for readability
```

## Comparison

### Street Map vs Aerial

| Feature | Street Map | Aerial Imagery |
|---------|------------|----------------|
| **Street names** | ✅ Yes | ❌ No (use Hybrid) |
| **Property view** | ❌ No | ✅ Yes (actual photos) |
| **Building detail** | ❌ Basic outline | ✅ Actual buildings |
| **Vegetation** | ❌ No | ✅ Yes |
| **Load speed** | ⚡ Fast | 🐢 Slower |
| **Data usage** | 💾 Low | 💾 Higher |
| **Property analysis** | ⭐ Basic | ⭐⭐⭐ Excellent |

### Best of Both: Hybrid Mode

- ✅ Aerial photos (property detail)
- ✅ Labels (street names, navigation)
- ✅ Roads highlighted
- ✅ Best for most use cases

## Advanced Features

### Compare Before/After

```
1. View property on Aerial
2. Toggle cadastral lots ON
3. Click lot for details
4. Note property info
5. Switch to Street Map
6. See labeled context
7. Switch back to Aerial
8. Analyze with context
```

### Screenshot/Print

```
For best screenshots:
1. Switch to Hybrid
2. Zoom to desired level
3. Center subject
4. Hide unneeded layers
5. Use browser screenshot tool
```

### Multiple Properties

```
For comparing properties:
1. Hybrid mode
2. Zoom to show both properties
3. Toggle cadastral lots
4. Click lots to identify
5. Analyze side-by-side on aerial
```

## API Details

### NSW Imagery Service

```
URL: https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer
Type: ArcGIS MapServer Tile Service
Format: Tiles (256x256 pixels)
CRS: Web Mercator (EPSG:3857)
Max Zoom: 21
Min Zoom: 6
```

### Tile URL Pattern

```
https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/tile/{z}/{y}/{x}

Where:
{z} = Zoom level (6-21)
{y} = Tile Y coordinate
{x} = Tile X coordinate
```

## Summary

✅ **What's Available:**
- Street Map (OpenStreetMap)
- Aerial Imagery (NSW SixMaps)
- Hybrid (Aerial + Labels)

✅ **How to Use:**
- Radio buttons in Layer Control Panel
- Instant switching
- Works with all other layers

✅ **Best Practices:**
- Use **Street** for navigation
- Use **Aerial** for property analysis
- Use **Hybrid** for most work
- Zoom to 16+ for best aerial quality

✅ **Perfect For:**
- Property valuation
- Site analysis
- Client presentations
- Market research
- Land use assessment

**Start using it now - just click the Aerial Imagery or Hybrid radio button!** 🛰️
