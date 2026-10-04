const { Pool } = require('pg');
require('dotenv').config({ path: '../.env' });

const poolConfig = {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    database: process.env.DB_NAME || 'groundwater_quality',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
    max: 20, // connection limit
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
};

if (process.env.DB_SSL === 'true') {
    poolConfig.ssl = { rejectUnauthorized: false };
}

const pool = new Pool(poolConfig);

module.exports = {
    query: (text, params) => pool.query(text, params),
};

