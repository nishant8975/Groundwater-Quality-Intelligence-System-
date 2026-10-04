const express = require('express');
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
        const data = rows[0];
        
        const pRes = await db.query(`
            SELECT 
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY wqi::double precision) as p75_wqi,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY wqi::double precision) as p95_wqi,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY wqi::double precision) as p99_wqi
            FROM wawqi_results WHERE wqi IS NOT NULL
        `);
        if (pRes.rows.length > 0) {
            data.p75_wqi = pRes.rows[0].p75_wqi;
            data.p95_wqi = pRes.rows[0].p95_wqi;
            data.p99_wqi = pRes.rows[0].p99_wqi;
        }

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
        const { state, district, category, min_wqi } = req.query;
        
        let where = [];
        let params = [];
        let pidx = 1;
        
        if (state) { where.push(`state ILIKE $${pidx++}`); params.push(state); }
        if (district) { where.push(`district ILIKE $${pidx++}`); params.push(district); }
        if (category) { where.push(`category ILIKE $${pidx++}`); params.push(category); }
        if (min_wqi !== undefined && min_wqi !== null && min_wqi !== '' && !isNaN(min_wqi)) { 
            where.push(`wqi >= $${pidx++}`); 
            params.push(parseFloat(min_wqi)); 
        }
        
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
        
        if (state) { where.push(`state ILIKE $${pidx++}`); params.push(state); }
        if (district) { where.push(`district ILIKE $${pidx++}`); params.push(district); }
        if (category) { where.push(`latest_category ILIKE $${pidx++}`); params.push(category); }
        
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

// 16. STATION INTELLIGENCE API LISTING AND SEARCH
const handleStationSearch = async (req, res, next) => {
    try {
        const { page, limit, offset } = getPaginationParams(req);
        const { search, q, state, district, data_quality, sort_by, order } = req.query;
        const searchTerm = (search || q || '').trim();

        let where = [];
        let params = [];
        let pidx = 1;

        if (searchTerm !== '') {
            where.push(`(station_name ILIKE $${pidx} OR district ILIKE $${pidx} OR state ILIKE $${pidx})`);
            params.push(`%${searchTerm}%`);
            pidx++;
        }
        if (state) {
            where.push(`state ILIKE $${pidx++}`);
            params.push(state);
        }
        if (district) {
            where.push(`district ILIKE $${pidx++}`);
            params.push(district);
        }
        if (data_quality) {
            where.push(`data_quality_class = $${pidx++}`);
            params.push(data_quality.toUpperCase().replace('_', ' '));
        }

        let whereClause = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';

        // Sorting options whitelist
        const allowedSorts = {
            'sample_count': 'sample_count',
            'wawqi_eligibility_percentage': 'wawqi_eligibility_percentage',
            'median_wqi': 'median_wqi',
            'station_name': 'station_name'
        };
        const sortColumn = allowedSorts[sort_by] || 'sample_count';
        const sortOrder = (order && order.toLowerCase() === 'asc') ? 'ASC' : 'DESC';

        const countQuery = `SELECT COUNT(*) FROM mv_station_identity ${whereClause}`;
        const countResult = await db.query(countQuery, params);
        const total = parseInt(countResult.rows[0].count);

        const dataQuery = `
            SELECT 
                station_hash, station_name, state, district, latitude, longitude,
                sample_count, first_sample_date, last_sample_date,
                wawqi_available_count, wawqi_unavailable_count, wawqi_eligibility_percentage,
                excellent_count, good_count, poor_count, very_poor_count, unsuitable_count,
                median_wqi, p90_wqi, max_wqi, latest_source_warning,
                historically_dominant_parameters, dominant_parameter_sample_count, dominant_parameter_percentage,
                data_quality_class, data_quality_reason
            FROM mv_station_identity 
            ${whereClause} 
            ORDER BY ${sortColumn} ${sortOrder} NULLS LAST, station_name ASC 
            LIMIT $${pidx++} OFFSET $${pidx++}
        `;
        params.push(limit, offset);

        const { rows } = await db.query(dataQuery, params);
        res.json(successResponse(rows, buildPaginationMeta(page, limit, total)));
    } catch (err) { next(err); }
};

router.get('/stations', validateState, handleStationSearch);
router.get('/stations/search', validateState, handleStationSearch);


// 17. STATION DETAIL API BY HASH
router.get('/stations/:hash', async (req, res, next) => {
    try {
        const { hash } = req.params;
        const stationResult = await db.query('SELECT * FROM mv_station_identity WHERE station_hash = $1', [hash]);
        if (stationResult.rows.length === 0) {
            return res.status(404).json(errorResponse('NOT_FOUND', 'Station not found.'));
        }
        const station = stationResult.rows[0];

        // Fetch sample history timeline
        const historyResult = await db.query(
            'SELECT sample_id, sample_date, wqi, category FROM vw_station_wawqi_history WHERE station_hash = $1 ORDER BY sample_date DESC NULLS LAST, sample_id DESC',
            [hash]
        );

        // Fetch parameter analytics profile
        const paramResult = await db.query(
            'SELECT parameter, observation_count, missing_count, minimum, median, maximum, p75, p90, exceedance_count, exceedance_percentage FROM mv_station_parameter_analytics WHERE station_hash = $1 ORDER BY parameter ASC',
            [hash]
        );

        res.json(successResponse({
            ...station,
            history: historyResult.rows,
            parameters: paramResult.rows
        }));
    } catch (err) { next(err); }
});

// 18. STATION HISTORY TIMELINE API
router.get('/stations/:hash/history', async (req, res, next) => {
    try {
        const { hash } = req.params;
        const { rows } = await db.query(
            'SELECT sample_id, sample_date, wqi, category FROM vw_station_wawqi_history WHERE station_hash = $1 ORDER BY sample_date DESC NULLS LAST, sample_id DESC',
            [hash]
        );
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

// 19. STATION PARAMETER PROFILE API
router.get('/stations/:hash/parameters', async (req, res, next) => {
    try {
        const { hash } = req.params;
        const { rows } = await db.query(
            'SELECT parameter, observation_count, missing_count, minimum, median, maximum, p75, p90, exceedance_count, exceedance_percentage FROM mv_station_parameter_analytics WHERE station_hash = $1 ORDER BY parameter ASC',
            [hash]
        );
        res.json(successResponse(rows));
    } catch (err) { next(err); }
});

module.exports = router;

