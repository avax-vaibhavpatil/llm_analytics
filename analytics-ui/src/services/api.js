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

/**
 * Register a non-matched/partial-matched query with admin
 * 
 * Called when AI cannot find all required columns for a query.
 * Saves the query details to database for admin review.
 * 
 * @param {Object} data - Query details
 * @param {string} data.original_query - User's original query text
 * @param {string} data.technical_interpretation - LLM's technical understanding
 * @param {string} data.table_name - Table user tried to query
 * @param {Array<string>} data.required_columns - Columns needed for analysis
 * @param {Array<string>} data.missing_columns - Columns that don't exist
 * @param {Array<string>} data.available_columns - Columns that do exist
 * @returns {Promise<Object>} - {success: boolean, request_id: number, message: string}
 * 
 * @example
 * const result = await registerAdminRequest({
 *   original_query: "give me date of birth of all customers",
 *   technical_interpretation: "User wants date_of_birth column...",
 *   table_name: "crm_customers",
 *   required_columns: ["date_of_birth"],
 *   missing_columns: ["date_of_birth"],
 *   available_columns: []
 * });
 * console.log(result.request_id); // 123
 */
export const registerAdminRequest = async (data) => {
  const response = await api.post('/admin/register-query', {
    original_query: data.original_query,
    technical_interpretation: data.technical_interpretation,
    table_name: data.table_name,
    required_columns: data.required_columns,
    missing_columns: data.missing_columns,
    available_columns: data.available_columns,
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

