import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Checkbox,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Divider,
  Grid,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  ArrowForward as ArrowIcon,
  ArrowBack as BackIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';
import { generateReport } from '../services/api';

function PreviewPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data from previous screen
  const { result, query, table } = location.state || {};

  // State for column selection
  // Initially, all available columns are selected (or empty if no result)
  const [selectedColumns, setSelectedColumns] = useState(
    result ? new Set(result.available_columns) : new Set()
  );
  
  // State for real data
  const [realData, setRealData] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [dataError, setDataError] = useState(null);

  // If no data, redirect to home (after hooks are called!)
  React.useEffect(() => {
    if (!result) {
      navigate('/');
    }
  }, [result, navigate]);
  
  // Fetch real data when selected columns change
  useEffect(() => {
    const fetchRealData = async () => {
      if (selectedColumns.size === 0 || !table) return;
      
      setLoadingData(true);
      setDataError(null);
      
      try {
        const columns = Array.from(selectedColumns);
        // ✅ Use SQL filters from LLM analysis instead of null!
        const filters = result?.sql_filters || null;
        const response = await generateReport(table, columns, filters, 5); // Get 5 rows for preview
        setRealData(response.data);
      } catch (error) {
        console.error('Error fetching real data:', error);
        setDataError(error.message || 'Failed to fetch data');
      } finally {
        setLoadingData(false);
      }
    };
    
    fetchRealData();
  }, [selectedColumns, table, result]);

  // Don't render if no data
  if (!result) {
    return null;
  }

  // Handle checkbox toggle
  const handleToggleColumn = (column) => {
    setSelectedColumns((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(column)) {
        newSet.delete(column);
      } else {
        newSet.add(column);
      }
      return newSet;
    });
  };

  const handleGenerateReport = () => {
    navigate('/report', { 
      state: { 
        result, 
        query, 
        table,
        selectedColumns: Array.from(selectedColumns)
      } 
    });
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <Sidebar />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          minHeight: '100vh',
        }}
      >
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          {/* Header */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" gutterBottom>
              📊 Report Preview & Configuration
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Select columns to include in your report
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {/* Left Side: Column Selection */}
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  ✏️ Column Selection
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                {/* Query Summary */}
                <Box sx={{ mb: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="caption" color="textSecondary">
                    Query:
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {query}
                  </Typography>
                  <Chip 
                    label={table} 
                    size="small" 
                    sx={{ mt: 1 }} 
                  />
                </Box>

                {/* Required Columns (Can't uncheck) */}
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Required Columns:
                </Typography>
                {result.required_columns
                  .filter(col => result.available_columns.includes(col))
                  .map((column) => (
                    <FormControlLabel
                      key={column}
                      control={
                        <Checkbox
                          checked={selectedColumns.has(column)}
                          onChange={() => handleToggleColumn(column)}
                          color="primary"
                        />
                      }
                      label={column}
                      sx={{ display: 'block', mb: 1 }}
                    />
                  ))
                }

                {/* Optional Columns (Can add/remove) */}
                {result.optional_columns && result.optional_columns.length > 0 && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      Optional Columns:
                    </Typography>
                    {result.optional_columns.map((column) => (
                      <FormControlLabel
                        key={column}
                        control={
                          <Checkbox
                            checked={selectedColumns.has(column)}
                            onChange={() => handleToggleColumn(column)}
                            color="secondary"
                          />
                        }
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {column}
                            <Chip 
                              label="Optional" 
                              size="small" 
                              sx={{ ml: 1, fontSize: '0.7rem' }} 
                            />
                          </Box>
                        }
                        sx={{ display: 'block', mb: 1 }}
                      />
                    ))}
                  </>
                )}

                <Alert severity="info" sx={{ mt: 3 }}>
                  {selectedColumns.size} column(s) selected
                </Alert>
              </Paper>
            </Grid>

            {/* Right Side: Sample Preview */}
            <Grid item xs={12} md={8}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📋 Real Data Preview (First 5 rows)
                </Typography>
                
                <Typography variant="caption" color="textSecondary" paragraph>
                  🔥 This is REAL data from your database!
                </Typography>

                {selectedColumns.size === 0 ? (
                  <Alert severity="warning">
                    Please select at least one column to preview
                  </Alert>
                ) : loadingData ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
                    <CircularProgress />
                    <Typography sx={{ ml: 2 }}>Loading real data...</Typography>
                  </Box>
                ) : dataError ? (
                  <Alert severity="error">
                    Error loading data: {dataError}
                  </Alert>
                ) : (
                  <>
                    <Alert severity="success" sx={{ mb: 2 }}>
                      ✅ Showing {realData.length} real rows from database
                    </Alert>
                    <TableContainer sx={{ maxHeight: 400 }}>
                      <Table stickyHeader size="small">
                        <TableHead>
                          <TableRow>
                            {Array.from(selectedColumns).map((column) => (
                              <TableCell 
                                key={column}
                                sx={{ 
                                  fontWeight: 'bold',
                                  bgcolor: 'primary.main',
                                  color: 'white'
                                }}
                              >
                                {column}
                              </TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {realData.length === 0 ? (
                            <TableRow>
                              <TableCell colSpan={selectedColumns.size} align="center">
                                <Typography color="textSecondary">No data found</Typography>
                              </TableCell>
                            </TableRow>
                          ) : (
                            realData.map((row, index) => (
                              <TableRow 
                                key={index}
                                sx={{ '&:hover': { bgcolor: '#f5f5f5' } }}
                              >
                                {Array.from(selectedColumns).map((column) => (
                                  <TableCell key={column}>
                                    {row[column] !== null && row[column] !== undefined ? String(row[column]) : 'N/A'}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}

                {/* Action Buttons */}
                <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'space-between' }}>
                  <Button
                    variant="outlined"
                    startIcon={<BackIcon />}
                    onClick={() => navigate('/availability', { state: { result, query, table } })}
                  >
                    Back
                  </Button>

                  <Button
                    variant="contained"
                    size="large"
                    endIcon={<ArrowIcon />}
                    onClick={handleGenerateReport}
                    disabled={selectedColumns.size === 0}
                  >
                    Generate Full Report
                  </Button>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}

export default PreviewPage;

/*
 * EXPLANATION:
 * 
 * KEY FEATURES:
 * 
 * 1. Column Selection (Left Side):
 *    - Checkboxes for required columns
 *    - Checkboxes for optional columns
 *    - Can add/remove any column
 *    - Counter shows how many selected
 * 
 * 2. Sample Preview (Right Side):
 *    - Mock data table (5 rows)
 *    - Shows only selected columns
 *    - Updates in real-time when you check/uncheck
 *    - Sticky header (stays visible when scrolling)
 * 
 * 3. Mock Data Generation:
 *    - generateMockData() creates realistic sample data
 *    - Different data types based on column name
 *    - mrr/revenue → dollar amounts
 *    - industry → business sectors
 *    - dates → formatted dates
 *    - Smart defaults for unknown columns
 * 
 * 4. State Management:
 *    - selectedColumns: Set of column names
 *    - Updates when checkbox clicked
 *    - Table re-renders automatically
 * 
 * 5. Validation:
 *    - Generate button disabled if no columns selected
 *    - Shows warning if nothing selected
 * 
 * NEXT: Add the route to App.js!
 */

