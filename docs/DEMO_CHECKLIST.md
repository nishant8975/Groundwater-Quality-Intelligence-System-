# FINAL DEMONSTRATION & PRESENTATION CHECKLIST

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## DEMO PREPARATION

Before presenting, ensure all services are initialized:
1. **PostgreSQL Service:** Running on port `5432` with database `groundwater_quality`.
2. **Backend API:** Express server running at `http://localhost:3000` (`cd backend && npm start`).
3. **Frontend Application:** Vite server running at `http://localhost:5173` (`cd frontend && npm run dev`).

---

## 17-STEP DEMONSTRATION SEQUENCE

| Step | Action / Page | Expected Result | Key Talking Point / Highlight |
| :-: | :--- | :--- | :--- |
| **1** | Open Dashboard (`/`) | National summary cards render instantly | Emphasize 165,162 water samples across 30 Indian States/UTs. |
| **2** | Review WAWQI Breakdown | Donut chart displays 5 categories | Highlight scientific WAWQI classification (Unsuitable = 24.04%). |
| **3** | Select State Filter | Filter dashboard to "Haryana" | Point out state-aware analytical context switching. |
| **4** | Open State Directory (`/states`) | Table displaying 30 States/UTs | Show mean WAWQI ratings and sample counts by state. |
| **5** | Open District Analytics (`/districts`) | Table listing 584 districts | Highlight top risk districts ranked by unsuitable percentage. |
| **6** | View Parameter Catalog (`/parameters`) | Table of 27 chemical parameters | Explain BIS IS 10500:2012 acceptable limits ($S_i$). |
| **7** | Open Exceedance Explorer (`/exceedances`) | Bar chart of exceedance rates | Point out highest exceedance parameters (Nitrate, Fluoride, EC). |
| **8** | Open Extreme Values (`/extremes`) | Table of extreme WQI values | Emphasize raw data transparency (Sample 1419 unclamped WQI $> 1.4\text{M}$). |
| **9** | Open Data Quality Page (`/data-quality`) | Completeness breakdown | Explain 44,424 WAWQI-unavailable samples ($\text{coverage} < 6$). |
| **10** | Open GIS Spatial Map (`/map`) | Interactive CartoDB dark map | Show 165,010 valid locations mapped with custom category markers. |
| **11** | Filter GIS Map | Select "Unsuitable" category filter | Demonstrate spatial clustering of poor quality groundwater points. |
| **12** | Click GIS Map Marker | Interactive popup appears | Show location coordinates, WQI score, and category status badge. |
| **13** | Open Station Directory (`/stations`) | Table of 22,753 canonical stations | Explain `DATA RICH` ($\ge 5$ params) vs `DATA LIMITED` ($< 5$) tiers. |
| **14** | Search Station Directory | Type "Patna" in search bar | Demonstrate sub-150 ms real-time station search. |
| **15** | Click Station Detail | Opens `/stations/:hash` view | Show station physical attributes and data quality badge. |
| **16** | View Station History | Recharts temporal line plot renders | Point out multi-year WAWQI trend for individual station. |
| **17** | Return to Overview (`/`) | Navigates cleanly back to root | Highlight single-page application speed and 0 console errors. |
