import React, { useState } from 'react';
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
} from '@mui/material';
import {
  ArrowForward as ArrowIcon,
  ArrowBack as BackIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';

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

  // If no data, redirect to home (after hooks are called!)
  React.useEffect(() => {
    if (!result) {
      navigate('/');
    }
  }, [result, navigate]);

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

  // Generate mock sample data for preview
  const generateMockData = () => {
    // Create 5 sample rows
    const mockData = [];
    const columns = Array.from(selectedColumns);
    
    for (let i = 0; i < 5; i++) {
      const row = {};
      columns.forEach((col) => {
        // Generate appropriate mock data based on column name
        if (col.includes('id')) {
          row[col] = `ID${1001 + i}`;
        } else if (col.includes('mrr') || col.includes('arr') || col.includes('amount') || col.includes('revenue')) {
          row[col] = `$${(Math.random() * 2000 + 500).toFixed(0)}`;
        } else if (col.includes('industry') || col.includes('sector')) {
          row[col] = ['Technology', 'Finance', 'Retail', 'Healthcare', 'Manufacturing'][i];
        } else if (col.includes('country')) {
          row[col] = ['USA', 'UK', 'Canada', 'Germany', 'France'][i];
        } else if (col.includes('date') || col.includes('created') || col.includes('updated')) {
          row[col] = new Date(2024, 5 + i, 1).toISOString().split('T')[0];
        } else if (col.includes('count') || col.includes('total')) {
          row[col] = Math.floor(Math.random() * 100) + 10;
        } else if (col.includes('name')) {
          row[col] = ['Acme Corp', 'Tech Solutions', 'Finance Plus', 'Retail Co', 'Health Inc'][i];
        } else {
          row[col] = `Sample ${i + 1}`;
        }
      });
      mockData.push(row);
    }
    
    return mockData;
  };

  const sampleData = generateMockData();

  const handleGenerateReport = () => {
    navigate('/report', { 
      state: { 
        result, 
        query, 
        table,
        selectedColumns: Array.from(selectedColumns),
        sampleData 
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
                  📋 Sample Preview (First 5 rows)
                </Typography>
                
                <Typography variant="caption" color="textSecondary" paragraph>
                  This is mock data for preview purposes
                </Typography>

                {selectedColumns.size === 0 ? (
                  <Alert severity="warning">
                    Please select at least one column to preview
                  </Alert>
                ) : (
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
                        {sampleData.map((row, index) => (
                          <TableRow 
                            key={index}
                            sx={{ '&:hover': { bgcolor: '#f5f5f5' } }}
                          >
                            {Array.from(selectedColumns).map((column) => (
                              <TableCell key={column}>
                                {row[column] || 'N/A'}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
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

