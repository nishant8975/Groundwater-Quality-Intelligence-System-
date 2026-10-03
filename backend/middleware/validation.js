const { errorResponse } = require('../utils/responseBuilder');

const validateState = (req, res, next) => {
    // This could be enhanced to check against a hardcoded list of Indian states, 
    // but for now we just sanitize standard injection risk.
    if (req.query.state && typeof req.query.state !== 'string') {
        return res.status(400).json(errorResponse('INVALID_PARAMETER', 'Invalid state parameter.'));
    }
    next();
};

module.exports = { validateState };
