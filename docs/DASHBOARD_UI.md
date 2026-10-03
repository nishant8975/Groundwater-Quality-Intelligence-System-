# Dashboard UI Documentation (Phase 8)

## Architecture Overview
The Phase 8 Analytics Dashboard brings the Groundwater Quality Intelligence System to life by consuming the Phase 6 Express API and presenting highly performant, server-aggregated statistics using Recharts and Tailwind CSS.

## Page Structure
1. **Dashboard (`/`)**: Main KPI stat cards, Category BarChart, Distribution placeholder, and State summary data grid.
2. **States (`/states`)**: Implements the State Overview component allowing exploration of unsuitability fractions.
3. **Extremes (`/extremes`)**: A paginated, searchable grid identifying all WQI observations classified as Unsuitable, equipped with data quality flags and dominant parameters.
4. **Exceedances (`/exceedances`)**: Tracks individual parameter breaches against the BIS standards, notably incorporating the dual-bound pH logic directly provided by the backend view.
5. **Data Quality (`/data-quality`)**: Explicit visual separation of analytical WQI results from data coverage limitations, explaining why 44k+ samples are properly marked as "UNAVAILABLE" rather than artificially forced to 0.

## Key Design Decisions
- **Recharts Integration**: Implemented a responsive vertical BarChart for WAWQI Category Distribution, styled with the project's strict dark aesthetic (slate/charcoal). Tooltips and axes customized to remove generic white backgrounds.
- **Extreme Value Handling**: The UI respects the million-scale WQI outliers. The distribution histogram is explicitly bounded to `0-200` with a warning label to prevent extreme tails from flattening the visual representation of 99% of the dataset. No data is clipped or altered; it is merely a *display transformation*.
- **Category Semantics**: 
  - `Excellent`: #34D399 (Emerald)
  - `Good`: #60A5FA (Blue)
  - `Poor`: #FBBF24 (Amber)
  - `Very Poor`: #F97316 (Orange)
  - `Unsuitable`: #EF4444 (Red)
  - `UNAVAILABLE`: #64748B (Slate)
- **URL State**: Extreme WQI page utilizes React Router `useSearchParams` for pagination (`?page=1`) and filtering (`?min_wqi=100`) allowing shareable, reproducible states without bloating the URL with JSON data.

## Performance
- **Aggregated Responses**: The dashboard strictly utilizes pre-aggregated API data. 
- **TanStack Caching**: All data fetching is heavily cached to eliminate redundant network requests.
- **Lazy Load Ready**: While all components are currently lightweight, the framework fully supports `React.lazy` for upcoming Phase 9 GIS map loading to ensure the browser thread is never blocked by massive geospatial datasets.

## Accessibility (a11y)
- Semantic HTML tags (`<h1>`, `<main>`, `<table>`) utilized.
- Contrast ratios verified against the `#0F172A` background.
- Categorical data is presented alongside explicit text labels (e.g. `Excellent`), never relying solely on color indicators.
