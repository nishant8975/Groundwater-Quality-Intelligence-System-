# STEP-BY-STEP SETUP GUIDE

## Groundwater Quality Intelligence — WAWQI Analytics Platform

---

## 1. PREREQUISITES

Ensure the following tools are installed on your machine:
* **Operating System:** Windows 10/11, macOS, or Linux
* **PostgreSQL:** Version 15.0 or higher (Default port: `5432`)
* **Node.js:** Version 18.0.0 or higher (Recommended: `v22.13.1`)
* **npm:** Version 9.0.0 or higher (Recommended: `11.1.0`)
* **Python:** Version 3.10 or higher (Required for ETL pipeline)
* **Git:** Installed and configured

---

## 2. REPOSITORY CLONING

```bash
git clone https://github.com/your-org/groundwater-quality-intelligence.git
cd "Groundwater Quality Intelligence System"
```

---

## 3. PYTHON ENVIRONMENT SETUP

Create and activate a isolated Python virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install pandas psycopg2-binary
```

---

## 4. POSTGRESQL DATABASE CREATION

Open your terminal or pgAdmin 4 and execute:

```sql
CREATE DATABASE groundwater_quality;
```

---

## 5. ENVIRONMENT CONFIGURATION

### Backend Environment Configuration
Create `backend/.env` from `.env.example`:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=groundwater_quality
DB_USER=postgres
DB_PASSWORD=your_postgres_password
PORT=3000
```

### Frontend Environment Configuration
Create `frontend/.env` from `.env.example`:

```bash
cd ../frontend
cp .env.example .env
```

Edit `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:3000/api
```

---

## 6. DATABASE SCHEMA & ANALYTICS EXECUTION

From the project root directory, run the SQL initialization scripts in sequence:

```bash
# Windows (PowerShell / CMD)
psql -U postgres -d groundwater_quality -f sql/01_schema.sql
psql -U postgres -d groundwater_quality -f sql/02_views.sql
psql -U postgres -d groundwater_quality -f sql/03_materialized_views.sql
psql -U postgres -d groundwater_quality -f sql/04_station_intelligence.sql

# Linux / macOS
psql -h localhost -U postgres -d groundwater_quality -f sql/01_schema.sql
psql -h localhost -U postgres -d groundwater_quality -f sql/02_views.sql
psql -h localhost -U postgres -d groundwater_quality -f sql/03_materialized_views.sql
psql -h localhost -U postgres -d groundwater_quality -f sql/04_station_intelligence.sql
```

---

## 7. ETL & WAWQI CALCULATION EXECUTION

To ingest raw CGWB CSV files into PostgreSQL and compute WAWQI scores:

```bash
# Execute ETL Ingestion Pipeline
python etl/01_ingest_cgwb.py

# Execute WAWQI Calculation Engine
python etl/02_wawqi_engine.py

# Refresh Materialized Views after data load
psql -U postgres -d groundwater_quality -c "REFRESH MATERIALIZED VIEW mv_station_identity;"
psql -U postgres -d groundwater_quality -c "REFRESH MATERIALIZED VIEW mv_wawqi_state_summary;"
psql -U postgres -d groundwater_quality -c "REFRESH MATERIALIZED VIEW mv_wawqi_district_summary;"
```

---

## 8. BACKEND REST API STARTUP

```bash
cd backend
npm install
npm start
```
*Expected Console Output:*
```text
Server running on port 3000
Connected to PostgreSQL database groundwater_quality
```

---

## 9. FRONTEND DASHBOARD STARTUP

In a new terminal window:

```bash
cd frontend
npm install
npm run dev
```
*Expected Console Output:*
```text
  VITE v8.3.2  ready in 240 ms

  ➜  Local:   http://localhost:5173/
```

---

## 10. SYSTEM VERIFICATION

1. **Backend Health Check:** Open `http://localhost:3000/api/health` in your browser. Expected: `{ "status": "UP", "database": "CONNECTED" }`.
2. **National Overview API:** Open `http://localhost:3000/api/overview`. Expected: JSON response containing 165,162 total samples.
3. **Frontend Dashboard UI:** Open `http://localhost:5173/` in your browser. Expected: Full interactive dashboard displaying national metrics, WAWQI category breakdown, and state filter.

---

## 11. TROUBLESHOOTING

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `ECONNREFUSED 127.0.0.1:5432` | PostgreSQL service not running | Start PostgreSQL service via `services.msc` or system command. |
| `psycopg2.OperationalError: password authentication failed` | Incorrect DB password | Check `DB_PASSWORD` in `backend/.env` and Python scripts. |
| `CORS Error` on frontend | API server not running on port 3000 | Ensure backend server is running before opening frontend. |
| GIS Map tiles not loading | Missing internet connection | Internet connection required for CartoDB tile retrieval. |
