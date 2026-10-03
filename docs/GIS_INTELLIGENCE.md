# Phase 9: GIS Intelligence

This document outlines the Phase 9 implementation of the Groundwater Quality Intelligence System's GIS features.

## 1. Map Architecture
The frontend leverages `react-leaflet` to visualize data delivered from the Phase 5/6 backend endpoint `/api/gis`.
All map processing resides in `frontend/src/pages/MapPage.tsx`.

## 2. GIS Data Source
The map consumes data exclusively from the existing Express REST API endpoint: `GET /api/gis`.
We intentionally do NOT transmit the entire 165,162 row dataset. Data is handled via offset-based pagination to maintain sub-second response times and manageable client DOM loads.

## 3. Marker Strategy & WAWQI Category Visualization
Leaflet `CircleMarker` elements are used rather than image-based markers for optimal performance.
The category of the WQI (e.g. Excellent, Poor, Unsuitable) determines the fill color of the circle, aligning completely with the semantic colors established in Phase 8.
- "UNAVAILABLE" WQI observations (due to missing mandatory parameters) are marked in slate/gray and handled safely without being zeroed out.

## 4. Popups & Data Quality
Each marker features a popup that lists:
- Station name
- State and District
- Computed WAWQI (or "Unavailable")
- Semantic Category
- Explicit Coordinates
- A subtle ⚠ warning if the WQI computation was flagged for "Insufficient parameters".
Note: No raw 1.6M parameter table observations are sent over the wire; we strictly use aggregated point features.

## 5. Map Bounds and Fit-to-Data
To handle wildly disparate geographies (e.g., Andaman vs. Punjab), the map introduces a `MapBoundsFitter` component. When new valid points load, the user can press "Fit to Data" to invoke `L.latLngBounds` and perfectly frame the visible markers.

## 6. Clustering Decision
Clustering was intentionally **NOT** introduced.
*Reasoning*: Because the API enforces pagination (defaulted to 100 per page on the frontend view), there are never more than a few hundred markers inserted into the Leaflet SVG pane at one time. Modern browser SVG engines can easily render <500 path elements without thread-blocking. Introducing `react-leaflet-cluster` would only bloat the bundle size and introduce overhead without meaningful UX gains on small paginated subsets.

## 7. Synchronized GIS Table
Directly below the map is a synchronized paginated list. It displays exactly the same observations that exist on the current map page, ensuring accessibility for screen readers and providing a rapid scanning mechanism for stations.

## 8. Cross-navigation
The `StateDetail` and `DistrictDetail` pages have been extended with "View on Map" buttons. Clicking these injects the State/District into the React Router URL search params, perfectly preserving the filter state on the Map.

## 9. Limitations & Next Steps
- We are currently limited by standard offset-pagination for geographic discovery. In a future iteration, the backend could be modified to support a Bounding-Box (`minLat`, `maxLat`, `minLng`, `maxLng`) query to natively retrieve stations based on map dragging (Viewport loading).
- No advanced interpolation or hotspot density maps are drawn yet (reserved for Phase 10).
