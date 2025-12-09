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

// Axios interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Something went wrong';
    throw new Error(message);
  }
);

export default api;

