const getPaginationParams = (req) => {
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
