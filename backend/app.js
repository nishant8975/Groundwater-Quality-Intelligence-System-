const express = require('express');
const cors = require('cors');
require('dotenv').config({ path: '../.env' }); // Load from root
const apiRoutes = require('./routes/api');
const { errorHandler } = require('./middleware/errorHandler');

const app = express();

// Configure CORS
const corsOptions = {
    origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));
app.use(express.json());

// Routes
app.use('/api', apiRoutes);

// Error Handling Middleware
app.use(errorHandler);

module.exports = app;
