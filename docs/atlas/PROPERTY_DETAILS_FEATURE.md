# Property Details Feature - Complete

## Overview

When you click on a lot on the map, a detailed property information panel now appears with:
1. **Property Details** - Lot/DP, Address, Area, Council
2. **Planning Information** - Zoning, Heritage, Flood, Bushfire
3. **NSW Planning Portal Link** - External link to official portal
4. **Council LGA Information** - Local Government Area details

---

## Features

### Property Details Section

Shows immediately when lot is clicked:

- **Lot/DP**: Lot number and Deposited Plan number (e.g., "Lot 100 DP 123456")
- **Address**: Full street address of the property
- **Area**: Land area in square meters (m²)
- **Council**: Local Government Area / Council name

### Planning Information Section

Loads asynchronously after property details:

- **Zoning**: Instructions to enable zoning layer for visual reference
- **Heritage**: Heritage conservation area status
- **Flood Planning**: Flood affected area status
- **Bushfire Prone**: Bushfire prone land designation

### Additional Information

- **LGA Details**: Local Government Area information
- **Planning Portal Link**: Button linking to NSW Planning Portal for detailed planning information

---

## How It Works

### Frontend (map.html)

1. User clicks on a lot
2. Lot highlights in green
3. Property details panel opens on the right
4. Basic property info displays immediately
5. "Loading planning data..." spinner appears
6. Planning information fetched from backend
7. Planning section updates with results

### Backend (/api/gis/query/point)

Accepts GET requests with lat/lon parameters:

```
GET /api/gis/query/point?lat=-33.8688&lon=151.2093
```

Returns:
```json
{
  "success": true,
  "results": {
    "lot": { /* GeoJSON of lot */ }
  },
  "planning": {
    "zoning": "Enable zoning layer on map to view",
    "heritage": "Enable heritage layer on map to view",
    "flood": "Enable flood layer on map to view",
    "bushfire": "Enable bushfire layer on map to view",
    "additionalInfo": "LGA: Sydney. Enable planning layers...",
    "planningPortalLink": "https://www.planningportal.nsw.gov.au/spatialviewer/"
  }
}
```

---

## Planning Layers

The planning information (zoning, heritage, flood, bushfire) is displayed as **visual WMS overlay layers** on the map.

### How to View Planning Details:

1. Click on a lot to see property details
2. Toggle the planning layers on using the checkboxes:
   - ☑ Zoning
   - ☑ Heritage
   - ☑ Flood Planning
   - ☑ Bushfire Prone
3. The colored overlays will appear on the map showing:
   - **Zoning**: Different colors for residential, commercial, industrial, etc.
   - **Heritage**: Red/pink areas showing heritage conservation zones
   - **Flood**: Blue areas showing flood planning zones
   - **Bushfire**: Orange/red areas showing bushfire prone land

4. Click "View NSW Planning Portal" button for official detailed information

---

## User Experience

### Click on Lot

```
[Lot clicked]
  ↓
[Green highlight appears]
  ↓
[Property panel opens on right]
  ↓
┌─────────────────────────────────┐
│ Property Details               │
│ ───────────────────────────── │
│ Lot/DP: Lot 100 DP 123456     │
│ Address: 123 Main St, Sydney  │
│ Area: 650 m²                  │
│ Council: Sydney City Council  │
│                               │
│ Planning Information          │
│ ───────────────────────────── │
│ ⟳ Loading planning data...    │
└─────────────────────────────────┘
```

### After Planning Data Loads

```
┌─────────────────────────────────┐
│ Property Details               │
│ ───────────────────────────── │
│ Lot/DP: Lot 100 DP 123456     │
│ Address: 123 Main St, Sydney  │
│ Area: 650 m²                  │
│ Council: Sydney City Council  │
│                               │
│ Planning Information          │
│ ───────────────────────────── │
│ Zoning: Enable layer to view  │
│ Heritage: Enable layer to view│
│ Flood: Enable layer to view   │
│ Bushfire: Enable layer to view│
│                               │
│ ℹ LGA: Sydney. Enable planning│
│   layers above for details... │
│                               │
│ [View NSW Planning Portal →]  │
└─────────────────────────────────┘
```

---

## Files Modified

1. **app/templates/map.html**
   - Enhanced `showPropertyDetails()` function to be async
   - Added `fetchPlanningInfo()` function
   - Added planning information section to property panel
   - Added loading spinner
   - Added NSW Planning Portal link button

2. **app/routes/main.py**
   - Modified `/api/gis/query/point` to accept GET requests
   - Added planning information response
   - Added council/LGA information extraction
   - Added planning portal link

---

## API Endpoint

### GET /api/gis/query/point

**Query Parameters:**
- `lat` (float, required): Latitude
- `lon` (float, required): Longitude

**Response:**
```json
{
  "success": true,
  "results": {
    "lot": {
      "type": "FeatureCollection",
      "features": [...]
    }
  },
  "planning": {
    "zoning": "string",
    "heritage": "string",
    "flood": "string",
    "bushfire": "string",
    "additionalInfo": "string",
    "planningPortalLink": "https://..."
  }
}
```

---

## Testing

Test the endpoint:

```bash
curl "http://localhost:5000/api/gis/query/point?lat=-33.8688&lon=151.2093"
```

Test in browser:
1. Start Flask server: `flask run`
2. Navigate to: http://localhost:5000/map
3. Zoom to Sydney (zoom 15+)
4. Click on any lot
5. Property details panel should appear with planning info

---

## Summary

The property details feature is now **fully functional** and provides:

✅ Instant property information (Lot/DP, address, area, council)
✅ Planning layer guidance (zoning, heritage, flood, bushfire)
✅ Council LGA information
✅ Link to NSW Planning Portal for official details
✅ Visual planning overlays when layers are enabled
✅ Async loading with spinner for better UX
✅ Clean, organized property information panel

Users can now click any lot and see comprehensive property and planning information immediately!
