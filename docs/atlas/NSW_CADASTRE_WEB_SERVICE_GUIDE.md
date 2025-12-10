# NSW Cadastre Web Service - Implementation Guide

## Overview

The GIS map now uses **NSW Spatial Services live web service** for cadastral lot boundaries, replacing the previous local Shapefile-based system. This provides:

- ✅ **State-wide coverage** - All of NSW, not just 30 LGAs
- ✅ **Always up-to-date** - Live data from NSW government
- ✅ **Better performance** - Dynamic loading, no local file storage
- ✅ **Official source** - Direct from NSW Spatial Services

## What Changed

### Before (Old System)
- 30 separate Shapefile layers (one per LGA)
- Required local storage of ~200+ MB data
- Manual updates needed
- Limited to specific LGAs
- Multiple API calls (one per LGA)

### After (New System)
- Single NSW Cadastre web service
- No local storage required
- Always current (live service)
- Full NSW coverage
- Single API call per view

## Service Details

### NSW Cadastre ArcGIS MapServer

**Service URL:**
```
https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer
```

**Lot Layer ID:** 6

**Service Type:** ArcGIS Feature Service (REST)

**Capabilities:**
- Query by bounding box
- Returns GeoJSON
- Max 1000 features per request
- Spatial reference: WGS84 (EPSG:4326)
- Scale range: 0 to 400,000

### Available Fields

The NSW Cadastre service provides these property attributes:

| Field | Description | Example |
|-------|-------------|---------|
| `lotnumber` / `LOTNUMBER` | Lot number | "123" |
| `planno` / `PLANNO` | Plan number | "DP 456789" |
| `planlabel` / `PLANLABEL` | Plan label | "DP 456789" |
| `address` / `ADDRESS` | Property address | "45 Smith St, Newtown NSW 2042" |
| `calcarea` / `CALCAREA` | Calculated area | 450.5 (m²) |
| `lga` / `LGA` | Local Government Area | "Inner West Council" |

## How It Works

### 1. User Toggles Cadastral Lots

When user checks "Property Lots (NSW Spatial Services)":

```javascript
cadastralLotsEnabled = true;
loadNSWCadastreInView();
```

### 2. Check Zoom Level

Only loads at zoom 15 or higher (performance optimization):

```javascript
const zoom = map.getZoom();
if (zoom < 15) {
    // Clear layer and return
    return;
}
```

### 3. Build Query URL

Constructs ArcGIS Feature Service query:

```javascript
const queryUrl = `${nswCadastreService}/${cadastralLotLayerId}/query`;
const params = new URLSearchParams({
    geometry: JSON.stringify({
        xmin: bounds.getWest(),
        ymin: bounds.getSouth(),
        xmax: bounds.getEast(),
        ymax: bounds.getNorth(),
        spatialReference: { wkid: 4326 }
    }),
    geometryType: 'esriGeometryEnvelope',
    spatialRel: 'esriSpatialRelIntersects',
    outFields: '*',
    returnGeometry: true,
    f: 'geojson',
    resultRecordCount: 1000
});
```

### 4. Fetch Data from Service

Makes single API call:

```javascript
const response = await fetch(url);
const data = await response.json();
// Returns GeoJSON with lot features
```

### 5. Render on Map

Converts GeoJSON to Leaflet layer:

```javascript
nswCadastreLayer = L.geoJSON(data, {
    style: {
        color: '#2c3e50',
        weight: 1.5,
        fillColor: '#ecf0f1',
        fillOpacity: 0.1
    },
    onEachFeature: function(feature, layer) {
        // Add popup with lot info
        layer.bindPopup(popupContent);
    }
});

nswCadastreLayer.addTo(map);
```

### 6. Auto-Update on Pan/Zoom

Reloads when map moves:

```javascript
map.on('moveend', function() {
    if (cadastralLotsEnabled) {
        setTimeout(loadNSWCadastreInView, 300);
    }
});

map.on('zoomend', function() {
    if (cadastralLotsEnabled) {
        loadNSWCadastreInView();
    }
});
```

## Usage

### Step 1: Navigate to Map

```
http://localhost:5000/map
```

### Step 2: Zoom to Your Area

- Navigate to any location in NSW
- Zoom to **level 15 or higher**
- Lower zoom = hidden (too many features)

### Step 3: Toggle Cadastral Lots

1. Find **"NSW Cadastre"** section in layer panel
2. Toggle **"Property Lots (NSW Spatial Services)"** ON
3. Lots automatically load for current view

### Step 4: Pan Around NSW

- **Pan to any area** - lots auto-load
- **Zoom in/out** - lots appear/disappear based on zoom
- **Click lots** - see property details

### Step 5: Click for Property Info

Click any lot to see popup:

```
Property Lot
─────────────
Lot: 123
Plan: DP 456789
Address: 45 Smith Street, Newtown NSW 2042
Area: 450.50 m²
LGA: Inner West Council
```

## Performance

### Zoom-Based Loading

| Zoom Level | Behavior | Reason |
|------------|----------|--------|
| < 15 | Lots hidden | Would be thousands of features |
| 15 | Lots visible | Moderate area (~200-400 lots) |
| 16 | Optimal | Small area (~100-200 lots) |
| 17-18 | Very detailed | Very small area (~20-100 lots) |

### Load Times

| Area Size | Features | Typical Load Time |
|-----------|----------|-------------------|
| Small (zoom 17) | 20-100 lots | 300-600ms |
| Medium (zoom 16) | 100-300 lots | 600-1200ms |
| Large (zoom 15) | 200-500 lots | 1000-2000ms |

### Max Features Limit

Service returns max **1000 features** per request:

- At zoom 15: May hit limit in dense urban areas
- At zoom 16+: Usually well under limit
- If limit hit: Zoom in to see all lots

### Debouncing

Pan events debounced by **300ms**:

```javascript
setTimeout(loadNSWCadastreInView, 300);
```

Prevents excessive API calls while panning.

## Integration with Other Layers

### Cadastre + Aerial Imagery

```
1. Select "Aerial Imagery" or "Hybrid" base map
2. Zoom to level 16+
3. Toggle "Property Lots" ON
4. Result: See lot boundaries on aerial photos
```

**Perfect for:**
- Property valuation
- Site analysis
- Building footprint analysis

### Cadastre + Planning Layers

```
1. Toggle "Zoning" ON (NSW Planning Portal)
2. Zoom to level 16+
3. Toggle "Property Lots" ON
4. Click lot → See both zoning and lot info
```

**Perfect for:**
- Development feasibility
- Planning constraints
- DA preparation

### Cadastre + Administrative Layers

```
1. Toggle "Suburbs" ON
2. Toggle "LGA Boundaries" ON
3. Zoom to level 16+
4. Toggle "Property Lots" ON
5. Result: Context + detail
```

**Perfect for:**
- Market research
- Regional analysis
- Understanding locality

## Troubleshooting

### Lots Don't Appear

**Check 1: Zoom Level**
```javascript
// Open browser console (F12)
console.log('Current zoom:', map.getZoom());
// Must be 15 or higher
```

**Check 2: Toggle State**
```
Ensure "Property Lots (NSW Spatial Services)" is checked/ON
```

**Check 3: Console Messages**
```
F12 → Console tab
Look for:
✓ "Loading NSW Cadastre lots from: https://..."
✓ "Loaded X cadastral lots from NSW service"

Errors:
✗ "Failed to load NSW Cadastre: ..."
✗ Network errors (check internet connection)
```

**Check 4: Service Availability**
```
Test service directly:
https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer
```

### Slow Performance

**Too zoomed out:**
- Zoom 15 loads many lots (200-500+)
- **Solution:** Zoom to 16 or 17

**Hitting 1000 feature limit:**
- Dense urban areas at zoom 15
- **Solution:** Zoom in further

**Network slow:**
- Service requires internet connection
- **Solution:** Check connection, wait for load

### Wrong or Missing Data

**Outside NSW:**
- Service only covers NSW
- Outside NSW boundary = no data

**Recently subdivided:**
- Service updated regularly but not instant
- Check SixMaps directly for most recent data

**CORS errors:**
- Service should allow cross-origin requests
- If issues, check browser console

### Lots Disappear When Panning

**Normal behavior:**
- Old layer cleared when loading new view
- Brief moment with no lots while loading
- **Wait 300-500ms** for new data to load

## API Query Examples

### Example 1: Query Lots in Newtown Area

```
GET https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer/6/query

Parameters:
{
  "geometry": {
    "xmin": 151.170,
    "ymin": -33.900,
    "xmax": 151.185,
    "ymax": -33.890,
    "spatialReference": { "wkid": 4326 }
  },
  "geometryType": "esriGeometryEnvelope",
  "spatialRel": "esriSpatialRelIntersects",
  "outFields": "*",
  "returnGeometry": true,
  "f": "geojson",
  "resultRecordCount": 1000
}
```

### Example 2: Response Format

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[151.175, -33.895], ...]]
      },
      "properties": {
        "lotnumber": "123",
        "planno": "DP 456789",
        "address": "45 Smith Street, Newtown NSW 2042",
        "calcarea": 450.5,
        "lga": "Inner West Council"
      }
    },
    ...
  ]
}
```

## Comparison: Old vs New

| Feature | Old System (Local) | New System (Web Service) |
|---------|-------------------|--------------------------|
| **Coverage** | 30 LGAs only | All of NSW |
| **Data freshness** | Static (manual update) | Live (always current) |
| **Storage** | ~200+ MB local | 0 MB (cloud service) |
| **API calls** | 30 per view (one/LGA) | 1 per view |
| **Setup** | Complex (30 layers) | Simple (one service) |
| **Maintenance** | Manual updates | None (maintained by NSW) |
| **Performance** | Local = fast | Network dependent |
| **Reliability** | 100% (local) | Depends on service uptime |
| **Data source** | SixMaps shapefiles | NSW Spatial Services API |

## Benefits

### ✅ Advantages of Web Service

1. **State-wide Coverage**
   - Access to all NSW cadastre
   - Not limited to specific LGAs
   - Consistent across regions

2. **Always Current**
   - Live data from NSW government
   - No manual updates needed
   - Reflects latest subdivisions

3. **Zero Storage**
   - No local Shapefile storage
   - Smaller application size
   - Easier deployment

4. **Single Source of Truth**
   - Official NSW government data
   - Same data as SixMaps website
   - Trusted and authoritative

5. **Simpler Code**
   - One service instead of 30 layers
   - Cleaner implementation
   - Easier maintenance

### ⚠️ Considerations

1. **Network Dependency**
   - Requires internet connection
   - Performance depends on network speed
   - Service outages affect availability

2. **Feature Limit**
   - Max 1000 features per request
   - May need higher zoom in dense areas

3. **No Offline Use**
   - Cannot work offline
   - Unlike local Shapefile data

## Advanced Usage

### Console Commands

```javascript
// Check current cadastre layer
console.log(nswCadastreLayer);

// Force reload
loadNSWCadastreInView();

// Check enabled state
console.log('Enabled:', cadastralLotsEnabled);

// Check zoom
console.log('Zoom:', map.getZoom());

// Get bounds
console.log('Bounds:', map.getBounds());
```

### Custom Styling

To change cadastre style, edit in map.html:

```javascript
nswCadastreLayer = L.geoJSON(data, {
    style: {
        color: '#2c3e50',        // Border color
        weight: 1.5,             // Border width
        fillColor: '#ecf0f1',    // Fill color
        fillOpacity: 0.1         // Fill transparency
    },
    ...
});
```

### Modify Popup Content

Customize property popup in `onEachFeature`:

```javascript
onEachFeature: function(feature, layer) {
    const props = feature.properties;
    let popupContent = '<div class="property-popup">';
    // Add custom fields here
    popupContent += '</div>';
    layer.bindPopup(popupContent);
}
```

## Summary

✅ **What's Working:**
- Live NSW Cadastre web service
- State-wide coverage (all NSW)
- Dynamic loading on pan/zoom
- Zoom 15+ requirement for performance
- Bbox filtering (only visible lots)
- Property info on click
- Integration with all other layers

✅ **How to Use:**
1. Navigate to any NSW location
2. Zoom to level 15+
3. Toggle "Property Lots (NSW Spatial Services)" ON
4. Lots automatically load for current view
5. Pan around - lots update automatically
6. Click lots for property details

✅ **Service Details:**
- Provider: NSW Spatial Services
- Type: ArcGIS Feature Service
- URL: maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer
- Layer: 6 (Lot)
- Format: GeoJSON
- Max features: 1000 per request

**Start using it now - toggle on and zoom in!** 🗺️

## Resources

- **NSW Spatial Services:** https://www.spatial.nsw.gov.au/
- **Data.NSW Portal:** https://data.nsw.gov.au/data/dataset/spatial-services-nsw-cadastre
- **Service Endpoint:** https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Cadastre/MapServer
- **SixMaps Website:** https://maps.six.nsw.gov.au/
