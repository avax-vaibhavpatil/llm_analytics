import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';

function HomePage() {
  const navigate = useNavigate();
  
  // State for form
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingTables, setLoadingTables] = useState(true);

  // Load tables when page loads
  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tables');
      const data = await response.json();
      setTables(data.tables);
      setLoadingTables(false);
    } catch (error) {
      console.error('Error loading tables:', error);
      setLoadingTables(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedTable || !query) {
      alert('Please select a table and enter a query');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/analyze/columns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          table_name: selectedTable,
          requirement: query,
        }),
      });

      const result = await response.json();
      
      // Navigate to processing page with the result
      navigate('/processing', { 
        state: { 
          result, 
          query, 
          table: selectedTable 
        } 
      });
      
    } catch (error) {
      console.error('Error:', error);
      alert('Error analyzing query. Make sure backend is running!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          minHeight: '100vh',
        }}
      >
        {/* Header */}
        <Typography variant="h4" gutterBottom>
          Welcome to Analytics Assistant
        </Typography>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Data Sources
                </Typography>
                <Typography variant="h4">
                  {tables.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Columns
                </Typography>
                <Typography variant="h4">
                  131
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Reports Generated
                </Typography>
                <Typography variant="h4">
                  0
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Reports Section */}
        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Recent Reports
        </Typography>
        <Typography color="textSecondary" paragraph>
          Your recent reports will appear here...
        </Typography>

        {/* Query Box at Bottom */}
        <Paper
          elevation={3}
          sx={{
            position: 'fixed',
            bottom: 20,
            left: 260, // Sidebar width + margin
            right: 20,
            p: 3,
            backgroundColor: '#f5f5f5',
          }}
        >
          <Typography variant="h6" gutterBottom>
            💬 Ask me anything about your data...
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            {/* Table Selector */}
            <Grid item xs={12} sm={3}>
              <TextField
                select
                fullWidth
                label="Select Table"
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                disabled={loadingTables}
              >
                {loadingTables ? (
                  <MenuItem disabled>Loading...</MenuItem>
                ) : (
                  tables.map((table) => (
                    <MenuItem key={table.table_name} value={table.table_name}>
                      {table.table_name} ({table.column_count} columns)
                    </MenuItem>
                  ))
                )}
              </TextField>
            </Grid>

            {/* Query Input */}
            <Grid item xs={12} sm={7}>
              <TextField
                fullWidth
                label="Your Question"
                placeholder='e.g. "Show me average MRR by industry"'
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAnalyze();
                  }
                }}
              />
            </Grid>

            {/* Analyze Button */}
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleAnalyze}
                disabled={loading || !selectedTable || !query}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze'}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Box>
  );
}

export default HomePage;

/*
 * EXPLANATION:
 * 
 * KEY SECTIONS:
 * 1. State Management:
 *    - tables: List of available tables from backend
 *    - selectedTable: Which table user picked
 *    - query: User's question
 *    - loading: Show spinner while processing
 * 
 * 2. useEffect Hook:
 *    - Runs when page loads
 *    - Fetches tables from API
 * 
 * 3. loadTables():
 *    - Calls backend: GET /api/tables
 *    - Updates state with result
 * 
 * 4. handleAnalyze():
 *    - Calls backend: POST /api/analyze/columns
 *    - Sends table_name and requirement
 *    - For now, just shows alert (next: navigate to processing page)
 * 
 * 5. Layout:
 *    - Sidebar (always visible)
 *    - Main content (stats, recent reports)
 *    - Query box (fixed at bottom)
 * 
 * NEXT STEP: Create the Processing page!
 */

