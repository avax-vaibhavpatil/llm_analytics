import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get list of all available tables
 * @returns {Promise<{tables: Array}>}
 */
export const getTables = async () => {
  const response = await api.get('/tables');
  return response.data;
};

/**
 * Get schema for a specific table
 * @param {string} tableName - Name of the table
 * @returns {Promise<Object>}
 */
export const getTableSchema = async (tableName) => {
  const response = await api.get(`/tables/${tableName}/schema`);
  return response.data;
};

/**
 * Analyze natural language requirement for columns
 * @param {string} tableName - Name of the table
 * @param {string} requirement - Natural language query
 * @returns {Promise<Object>}
 */
export const analyzeColumns = async (tableName, requirement) => {
  const response = await api.post('/analyze/columns', {
    table_name: tableName,
    requirement: requirement,
  });
  return response.data;
};

/**
 * Generate report with REAL DATA from database
 * @param {string} tableName - Name of the table
 * @param {Array<string>} columns - List of columns to include
 * @param {Object} filters - Optional filters (e.g., {segment: 'Enterprise'})
 * @param {number} limit - Maximum number of rows (default: 100)
 * @returns {Promise<Object>}
 */
export const generateReport = async (tableName, columns, filters = null, limit = 100) => {
  const response = await api.post('/reports/generate', {
    table_name: tableName,
    columns: columns,
    filters: filters,
    limit: limit,
  });
  return response.data;
};

// Axios interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Something went wrong';
    throw new Error(message);
  }
);

export default api;

