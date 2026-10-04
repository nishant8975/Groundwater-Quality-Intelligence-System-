# Complete Step-by-Step Production Deployment Guide
**Groundwater Quality Intelligence — WAWQI Analytics Platform**

Target Architecture:
`Vercel (React Frontend) -> Render (Express REST API) -> Supabase (PostgreSQL Database)`

---

## Step 1 — Push Workspace to GitHub
Ensure `.env` and `frontend/.env.local` are untracked by Git:
```powershell
git status
```
Commit changes and push to your GitHub repository:
```powershell
git add .
git commit -m "prepare project for production deployment"
git push origin main
```

---

## Step 2 — Create Supabase PostgreSQL Project
1. Log in to [Supabase](https://supabase.com).
2. Click **New Project** and configure your database region and password.
3. Once provisioned, open **Project Settings → Database → Connection String** to retrieve your:
   - `DB_HOST` (e.g., `db.xxxx.supabase.co`)
   - `DB_PORT` (`5432`)
   - `DB_NAME` (`postgres`)
   - `DB_USER` (`postgres.xxxx`)
   - `DB_PASSWORD`
4. In the **SQL Editor**, execute:
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_trgm;
   ```

---

## Step 3 — Export Local PostgreSQL Database & Restore to Supabase
1. Run `pg_dump` to create a custom binary dump:
   ```powershell
   pg_dump -h localhost -p 5432 -U postgres -d groundwater_quality --no-owner --no-privileges -Fc -f groundwater_quality.dump
   ```
2. Restore the dump to Supabase:
   ```powershell
   pg_restore -h YOUR_SUPABASE_HOST -p 5432 -U YOUR_SUPABASE_USER -d postgres --no-owner --no-privileges groundwater_quality.dump
   ```

---

## Step 4 — Database Reconciliation Verification
Run the validation script in the Supabase SQL Editor:
```sql
SELECT 'Samples' as metric, COUNT(*) as count FROM water_samples
UNION ALL SELECT 'EAV Observations', COUNT(*) FROM sample_parameter_values
UNION ALL SELECT 'WAWQI Available', COUNT(*) FROM wawqi_results WHERE wqi IS NOT NULL
UNION ALL SELECT 'Canonical Stations', COUNT(*) FROM mv_station_identity;
```
Verify:
- **Samples:** 165,162
- **EAV Observations:** 1,609,277
- **WAWQI Available:** 120,738
- **Canonical Stations:** 22,753

---

## Step 5 — Deploy Backend API to Render
1. Log in to [Render](https://render.com).
2. Click **New → Web Service** and connect your GitHub repository.
3. Configure the Web Service:
   - **Name:** `groundwater-quality-api`
   - **Runtime:** `Node`
   - **Root Directory:** `backend`
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
4. Add Environment Variables under **Environment**:
   - `DB_HOST` = `your-supabase-host`
   - `DB_PORT` = `5432`
   - `DB_NAME` = `postgres`
   - `DB_USER` = `your-supabase-user`
   - `DB_PASSWORD` = `your-supabase-password`
   - `DB_SSL` = `true`
   - `CORS_ORIGIN` = `http://localhost:5173` *(Temporary until Vercel URL is generated)*
5. Click **Create Web Service**. Render will deploy your Express API (e.g. `https://groundwater-quality-api.onrender.com`).

---

## Step 6 — Test Render Backend API Health
Open your Render API URL in a browser or curl:
- `https://YOUR-RENDER-API.onrender.com/api/health` -> Should return `{"status":"ok","database":"connected"}`
- `https://YOUR-RENDER-API.onrender.com/api/overview` -> Should return overview statistics JSON.

---

## Step 7 — Deploy Frontend UI to Vercel
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New → Project** and import your GitHub repository.
3. Configure Project Settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add Environment Variables under **Environment Variables**:
   - `VITE_API_BASE_URL` = `https://YOUR-RENDER-API.onrender.com/api`
   - `VITE_CARTO_API_KEY` = `YOUR_CARTO_KEY`
5. Click **Deploy**. Vercel will build and publish your frontend (e.g. `https://groundwater-quality.vercel.app`).

---

## Step 8 — Configure Production CORS on Render
1. Copy your live Vercel URL (e.g. `https://groundwater-quality.vercel.app`).
2. Go back to your **Render Dashboard → Web Service → Environment**.
3. Update:
   - `CORS_ORIGIN` = `https://groundwater-quality.vercel.app` *(no trailing slash)*
4. Save changes and redeploy the Render service.

---

## Step 9 — Production QA Checklist
- [x] Homepage & Dashboard load without errors
- [x] WAWQI Statistical Summary displays exact percentiles (Min 0.01, Median 68.52, P75 98.15, P95 376.64, P99 2719.21)
- [x] State & District analytics load from Supabase
- [x] GIS map loads CARTO tiles & displays location markers
- [x] Station search finds stations using trigram index (`pg_trgm`)
- [x] Direct React Router links (`/states`, `/districts`, `/parameters`, `/map`, `/stations`, `/data-quality`) load cleanly without Vercel 404s (handled via `vercel.json` SPA rewrite)
- [x] No credentials or API keys exposed in public source control
