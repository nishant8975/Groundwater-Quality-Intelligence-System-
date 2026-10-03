import os

files = {
    'backend/server.js': """const app = require('./app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
""",

    'backend/app.js': """const express = require('express');
const cors = require('cors');
require('dotenv').config({ path: '../.env' }); // Load from root
const apiRoutes = require('./routes/api');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();

// Configure CORS
const corsOptions = {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));
app.use(express.json());

// Routes
app.use('/api', apiRoutes);

// Error Handling Middleware
app.use(errorHandler);

module.exports = app;
""",

    'backend/db/index.js': """const { Pool } = require('pg');
require('dotenv').config({ path: '../.env' });

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'groundwater_quality',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
    max: 20, // connection limit
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

module.exports = {
    query: (text, params) => pool.query(text, params),
};
""",

    'backend/utils/responseBuilder.js': """const successResponse = (data, pagination = null) => {
    const response = { data };
    if (pagination) {
        response.pagination = pagination;
    }
    return response;
};

const errorResponse = (code, message) => {
    return {
        error: {
            code,
            message
        }
    };
};

module.exports = { successResponse, errorResponse };
""",

    'backend/utils/pagination.js': """const getPaginationParams = (req) => {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(500, Math.max(1, parseInt(req.query.limit) || 50));
    const offset = (page - 1) * limit;
    return { page, limit, offset };
};

const buildPaginationMeta = (page, limit, totalRows) => {
    return {
        page,
        limit,
        total: parseInt(totalRows, 10),
        totalPages: Math.ceil(totalRows / limit)
    };
};

module.exports = { getPaginationParams, buildPaginationMeta };
""",

    'backend/middleware/errorHandler.js': """const { errorResponse } = require('../utils/responseBuilder');

const errorHandler = (err, req, res, next) => {
    console.error(err);
    if (err.name === 'ValidationError') {
        return res.status(400).json(errorResponse('INVALID_PARAMETER', err.message));
    }
    res.status(500).json(errorResponse('INTERNAL_SERVER_ERROR', 'An unexpected error occurred.'));
};

module.exports = { errorHandler };
""",

    'backend/middleware/validation.js': """const { errorResponse } = require('../utils/responseBuilder');

const validateState = (req, res, next) => {
    // This could be enhanced to check against a hardcoded list of Indian states, 
    // but for now we just sanitize standard injection risk.
    if (req.query.state && typeof req.query.state !== 'string') {
        return res.status(400).json(errorResponse('INVALID_PARAMETER', 'Invalid state parameter.'));
    }
    next();
};

module.exports = { validateState };
""",

    'backend/routes/api.js': """const express = require('express');
const router = express.Router();
const db = require('../db');
const { successResponse, errorResponse } = require('../utils/responseBuilder');
const { getPaginationParams, buildPaginationMeta } = require('../utils/pagination');
const { validateState } = require('../middleware/validation');

// 4. HEALTH ENDPOINT
router.get('/health', async (req, res, next) => {
    try {
        const result = await db.query('SELECT 1 as up');
        res.json({
            status: 'ok',
            database: 'connected',
            timestamp: new Date().toISOString(),
            service: 'groundwater-quality-api'
        });
    } catch (error) {
        res.status(503).json(errorResponse('SERVICE_UNAVAILABLE', 'Database connection failed.'));
    }
});

// 5. NATIONAL OVERVIEW
router.get('/overview', async (req, res, next) => {
    try {
        const { rows } = await db.query('SELECT * FROM vw_wawqi_national_summary LIMIT 1');
        if (rows.length === 0) return res.json(successResponse({}));
        // Map decimal values to numbers for cleaner JSON
        const data = rows[0];
        Object.keys(data).forEach(k => {
            if (typeof data[k] === 'string' && !isNaN(data[k])) data[k] = parseFloat(data[k]);
        });
        res.json(successResponse(data));
    } catch (err) { next(err); }
});

// 6. WAWQI CATEGORY API
router.get('/wawqi/categories', async (req, res, next) => {
    try {
        const { rows } = await db.query(`
            SELECT wqi_category as category, COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM wawqi_results), 2) as percentage
            FROM vw_wawqi_categories
            GROUP BY wqi_category
            ORDER BY 
                CASE wqi_category 
                    WHEN 'Excellent' THEN 1
                    WHEN 'Good' THEN 2
                    WHEN 'Poor' THEN 3
                    WHEN 'Very Poor' THEN 4
                    WHEN 'Unsuitable' THEN 5
                    ELSE 6 
                END
        `);
        res.json(successResponse(rows.map(r => ({...r, count: parseInt(r.count), percentage: parseFloat(r.percentage)}))));
    } catch (err) { next(err); }
});

// 7. STATE API
router.get('/states', async (req, res, next) => {
    try {
        const { rows } = await db.query('SELECT * FROM mv_wawqi_state_summary ORDER BY state ASC');
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

// 8. STATE DETAIL
router.get('/states/:state', async (req, res, next) => {
    try {
        const { state } = req.params;
        const { rows } = await db.query('SELECT * FROM mv_wawqi_state_summary WHERE state = $1', [state]);
        if (rows.length === 0) {
            return res.status(404).json(errorResponse('NOT_FOUND', 'State not found.'));
        }
        res.json(successResponse(rows[0]));
    } catch (err) { next(err); }
});

// 9. DISTRICT API
router.get('/districts', validateState, async (req, res, next) => {
    try {
        const { state } = req.query;
        let query = 'SELECT * FROM mv_wawqi_district_summary';
        let params = [];
        if (state) {
            query += ' WHERE state = $1';
            params.push(state);
        }
        query += ' ORDER BY state ASC, district ASC';
        const { rows } = await db.query(query, params);
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

router.get('/districts/:district', async (req, res, next) => {
    try {
        const { district } = req.params;
        const { state } = req.query;
        let query = 'SELECT * FROM mv_wawqi_district_summary WHERE district = $1';
        let params = [district];
        if (state) {
            query += ' AND state = $2';
            params.push(state);
        }
        const { rows } = await db.query(query, params);
        if (rows.length === 0) {
            return res.status(404).json(errorResponse('NOT_FOUND', 'District not found.'));
        }
        res.json(successResponse(rows)); // Might return multiple if district name overlaps without state
    } catch (err) { next(err); }
});

// 10. PARAMETER API
router.get('/parameters', async (req, res, next) => {
    try {
        // Return parameters with standard limits
        const { rows } = await db.query(`
            SELECT p.canonical_name, p.display_name
            FROM parameters p
            WHERE p.canonical_name IN ('ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium')
        `);
        // Attach static standards metadata for simplicity as documented
        const standards = {
            'ph': { unit: 'pH', standard: '6.5 - 8.5', limit_type: 'Acceptable limit' },
            'chloride': { unit: 'mg/L', standard: 250, limit_type: 'Acceptable limit' },
            'sulphate': { unit: 'mg/L', standard: 200, limit_type: 'Acceptable limit' },
            'hardness': { unit: 'mg/L', standard: 200, limit_type: 'Acceptable limit' },
            'calcium': { unit: 'mg/L', standard: 75, limit_type: 'Acceptable limit' },
            'magnesium': { unit: 'mg/L', standard: 30, limit_type: 'Acceptable limit' },
            'iron': { unit: 'mg/L', standard: 0.3, limit_type: 'Acceptable limit' },
            'arsenic': { unit: 'mg/L', standard: 0.01, limit_type: 'Acceptable limit (Health-based)' },
            'uranium': { unit: 'mg/L', standard: 0.03, limit_type: 'Acceptable limit (Health-based)' }
        };
        const data = rows.map(r => ({
            ...r,
            ...standards[r.canonical_name]
        }));
        res.json(successResponse(data));
    } catch (err) { next(err); }
});

router.get('/parameters/:parameter', validateState, async (req, res, next) => {
    try {
        const { parameter } = req.params;
        const { state, district } = req.query;
        let query = 'SELECT * FROM mv_parameter_analytics WHERE canonical_name = $1';
        let params = [parameter];
        let pidx = 2;
        
        if (state) {
            query += ` AND state = $${pidx++}`;
            params.push(state);
        }
        if (district) {
            query += ` AND district = $${pidx++}`;
            params.push(district);
        }
        
        const { rows } = await db.query(query, params);
        if (rows.length === 0) return res.status(404).json(errorResponse('NOT_FOUND', 'Parameter data not found for given filters.'));
        
        // Aggregate if multiple rows returned (e.g. national level)
        // Since mv_parameter_analytics is grouped by state, district, we must sum/avg it here or build a national view.
        // For accurate percentiles, we'd need a different view, but for count/mean it's straightforward.
        // Actually, the simplest for the API is to return the matching rows and let the client aggregate, 
        // OR construct a dynamic aggregation query on sample_parameter_values.
        // Since we want to use the materialized views as much as possible:
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

// 11. EXCEEDANCE API
router.get('/exceedances', validateState, async (req, res, next) => {
    try {
        const { state, district, parameter } = req.query;
        let query = 'SELECT canonical_name as parameter, SUM(valid_measurement_count) as valid_measurement_count, SUM(exceedance_count) as exceedance_count FROM mv_parameter_exceedance WHERE 1=1';
        let params = [];
        let pidx = 1;
        
        if (state) { query += ` AND state = $${pidx++}`; params.push(state); }
        if (district) { query += ` AND district = $${pidx++}`; params.push(district); }
        if (parameter) { query += ` AND canonical_name = $${pidx++}`; params.push(parameter); }
        
        query += ' GROUP BY canonical_name';
        
        const { rows } = await db.query(query, params);
        const data = rows.map(r => {
            const count = parseInt(r.exceedance_count);
            const total = parseInt(r.valid_measurement_count);
            return {
                parameter: r.parameter,
                valid_observation_count: total,
                exceedance_count: count,
                exceedance_percentage: total > 0 ? parseFloat((count * 100 / total).toFixed(2)) : 0
            };
        });
        res.json(successResponse(data));
    } catch (err) { next(err); }
});

// 12. EXTREME WAWQI API
router.get('/extremes', validateState, async (req, res, next) => {
    try {
        const { page, limit, offset } = getPaginationParams(req);
        const { state, district, min_wqi } = req.query;
        
        let where = [];
        let params = [];
        let pidx = 1;
        
        if (state) { where.push(`state = $${pidx++}`); params.push(state); }
        if (district) { where.push(`district = $${pidx++}`); params.push(district); }
        if (min_wqi && !isNaN(min_wqi)) { where.push(`wqi >= $${pidx++}`); params.push(parseFloat(min_wqi)); }
        
        let whereClause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';
        
        const countQuery = `SELECT COUNT(*) FROM vw_wawqi_extreme_values ${whereClause}`;
        const countResult = await db.query(countQuery, params);
        const total = countResult.rows[0].count;
        
        const dataQuery = `SELECT * FROM vw_wawqi_extreme_values ${whereClause} ORDER BY wqi DESC LIMIT $${pidx++} OFFSET $${pidx++}`;
        params.push(limit, offset);
        
        const { rows } = await db.query(dataQuery, params);
        res.json(successResponse(rows, buildPaginationMeta(page, limit, total)));
    } catch (err) { next(err); }
});

// 13. GIS API
router.get('/gis', validateState, async (req, res, next) => {
    try {
        const { page, limit, offset } = getPaginationParams(req);
        const { state, district, category } = req.query;
        
        let where = [];
        let params = [];
        let pidx = 1;
        
        if (state) { where.push(`state = $${pidx++}`); params.push(state); }
        if (district) { where.push(`district = $${pidx++}`); params.push(district); }
        if (category) { where.push(`latest_category = $${pidx++}`); params.push(category); }
        
        let whereClause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';
        
        const countQuery = `SELECT COUNT(*) FROM vw_gis_points ${whereClause}`;
        const countResult = await db.query(countQuery, params);
        const total = countResult.rows[0].count;
        
        const dataQuery = `SELECT location_id, station_name, state, district, latitude, longitude, latest_sample_date, latest_wqi as wqi, latest_category as category FROM vw_gis_points ${whereClause} ORDER BY location_id ASC LIMIT $${pidx++} OFFSET $${pidx++}`;
        params.push(limit, offset);
        
        const { rows } = await db.query(dataQuery, params);
        res.json(successResponse(rows, buildPaginationMeta(page, limit, total)));
    } catch (err) { next(err); }
});

// 14. TEMPORAL API
router.get('/temporal', async (req, res, next) => {
    try {
        // Since mv_temporal_analytics is global by year, we just return it.
        const { rows } = await db.query('SELECT * FROM mv_temporal_analytics ORDER BY sample_year ASC');
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

// 15. DATA QUALITY API
router.get('/data-quality', async (req, res, next) => {
    try {
        const { rows } = await db.query('SELECT * FROM vw_data_quality_analytics LIMIT 1');
        // Fetch Sample 1419 specifically as required
        const anomaly = await db.query("SELECT sample_id, data_quality_flags FROM wawqi_results WHERE sample_id = 1419");
        
        const data = rows[0] || {};
        Object.keys(data).forEach(k => { data[k] = parseInt(data[k]); });
        
        data.flagged_sample_1419 = anomaly.rows[0] ? anomaly.rows[0].data_quality_flags : null;
        
        res.json(successResponse(data));
    } catch (err) { next(err); }
});

module.exports = router;
"""
}

# Create directories
os.makedirs('backend/db', exist_ok=True)
os.makedirs('backend/routes', exist_ok=True)
os.makedirs('backend/middleware', exist_ok=True)
os.makedirs('backend/utils', exist_ok=True)

# Write files
for filepath, content in files.items():
    with open(filepath, 'w') as f:
        f.write(content)

print("Backend files generated successfully.")
