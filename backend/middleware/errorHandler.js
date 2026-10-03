const { errorResponse } = require('../utils/responseBuilder');

const errorHandler = (err, req, res, next) => {
    console.error(err);
    if (err.name === 'ValidationError') {
        return res.status(400).json(errorResponse('INVALID_PARAMETER', err.message));
    }
    res.status(500).json(errorResponse('INTERNAL_SERVER_ERROR', 'An unexpected error occurred.'));
};

module.exports = { errorHandler };
