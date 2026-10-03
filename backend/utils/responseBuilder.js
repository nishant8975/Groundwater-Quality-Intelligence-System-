const successResponse = (data, pagination = null) => {
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
