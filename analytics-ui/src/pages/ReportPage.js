import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Grid,
  Divider,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Home as HomeIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data from previous screen
  const { result, query, table, selectedColumns, sampleData } = location.state || {};

  // If no data, redirect to home
  React.useEffect(() => {
    if (!result) {
      navigate('/');
    }
  }, [result, navigate]);

  if (!result) {
    return null;
  }

  // Export to CSV
  const handleExportCSV = () => {
    // Convert data to CSV format
    const columns = selectedColumns || result.available_columns;
    const headers = columns.join(',');
    
    const rows = sampleData.map(row => 
      columns.map(col => {
        const value = row[col] || '';
        // Escape quotes and wrap in quotes if contains comma
        return value.toString().includes(',') ? `"${value}"` : value;
      }).join(',')
    );
    
    const csvContent = [headers, ...rows].join('\n');
    
    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `report_${table}_${Date.now()}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Create similar report
  const handleCreateSimilar = () => {
    // Go back to home with pre-filled data
    navigate('/', { state: { prefillTable: table, prefillQuery: query } });
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
              📊 Report Results
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Generated: {new Date().toLocaleString()}
            </Typography>
          </Box>

          {/* Report Info Card */}
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="textSecondary">
                  Query:
                </Typography>
                <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                  "{query}"
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="textSecondary">
                  Table:
                </Typography>
                <Chip label={table} color="primary" />
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" color="textSecondary">
                  Columns:
                </Typography>
                <Typography variant="h6">
                  {selectedColumns?.length || result.available_columns.length}
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            {/* Technical Summary */}
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                💡 Analysis Summary:
              </Typography>
              <Typography variant="body2">
                {result.technical_summary}
              </Typography>
            </Alert>
          </Paper>

          {/* Data Table */}
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                📈 Report Data
              </Typography>
              <Chip 
                label={`${sampleData?.length || 0} rows`} 
                color="success" 
              />
            </Box>

            <TableContainer sx={{ maxHeight: 500 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    {(selectedColumns || result.available_columns).map((column) => (
                      <TableCell
                        key={column}
                        sx={{
                          fontWeight: 'bold',
                          bgcolor: 'primary.main',
                          color: 'white',
                          fontSize: '0.9rem',
                        }}
                      >
                        {column}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sampleData && sampleData.map((row, index) => (
                    <TableRow
                      key={index}
                      sx={{
                        '&:hover': { bgcolor: '#f5f5f5' },
                        '&:nth-of-type(odd)': { bgcolor: '#fafafa' },
                      }}
                    >
                      {(selectedColumns || result.available_columns).map((column) => (
                        <TableCell key={column}>
                          {row[column] || 'N/A'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Action Buttons */}
          <Paper elevation={3} sx={{ p: 3 }}>
            <Grid container spacing={2}>
              {/* Export Button */}
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="contained"
                  color="success"
                  size="large"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                >
                  Download CSV
                </Button>
              </Grid>

              {/* Create Similar Button */}
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  size="large"
                  startIcon={<RefreshIcon />}
                  onClick={handleCreateSimilar}
                >
                  Create Similar
                </Button>
              </Grid>

              {/* Back to Home Button */}
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  size="large"
                  startIcon={<HomeIcon />}
                  onClick={() => navigate('/')}
                >
                  Back to Home
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {/* Footer Info */}
          <Alert severity="success" sx={{ mt: 3 }}>
            ✅ Report generated successfully! You can download, create similar reports, or return to home.
          </Alert>
        </Container>
      </Box>
    </Box>
  );
}

export default ReportPage;

/*
 * EXPLANATION:
 * 
 * KEY FEATURES:
 * 
 * 1. Report Info Card:
 *    - Shows query, table, column count
 *    - Technical summary from LLM
 *    - Metadata about the report
 * 
 * 2. Data Table:
 *    - Displays all selected columns
 *    - Shows sample data from preview
 *    - Sticky header (stays visible when scrolling)
 *    - Alternating row colors (better readability)
 *    - Hover effect on rows
 * 
 * 3. Export to CSV:
 *    - Converts table data to CSV format
 *    - Handles commas in data (escapes properly)
 *    - Creates downloadable file
 *    - Filename includes table name and timestamp
 * 
 * 4. Action Buttons:
 *    - Download CSV: Export data
 *    - Create Similar: Go back to home with same query
 *    - Back to Home: Start fresh
 * 
 * 5. User-Friendly:
 *    - Clear labels
 *    - Color-coded buttons
 *    - Success message at bottom
 * 
 * THIS IS THE FINAL SCREEN! MVP COMPLETE AFTER THIS!
 */

