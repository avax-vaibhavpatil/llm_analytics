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
  Alert,
  AlertTitle,
  Chip,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import StorageIcon from '@mui/icons-material/Storage';
import DataObjectIcon from '@mui/icons-material/DataObject';
import BarChartIcon from '@mui/icons-material/BarChart';
import SearchIcon from '@mui/icons-material/Search';

function HomePage() {
  const navigate = useNavigate();
  
  // State for form
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingTables, setLoadingTables] = useState(true);
  const [error, setError] = useState(null);

  // Load tables when page loads
  useEffect(() => {
    loadTables();
  }, []);

  const loadTables = async () => {
    try {
      setError(null);
      setLoadingTables(true);
      
      const response = await fetch('http://localhost:8000/api/tables');
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}. Is the backend running?`);
      }
      
      const data = await response.json();
      console.log('Tables loaded:', data);
      
      setTables(data.tables || []);
      
      // Auto-select first table if available
      if (data.tables && data.tables.length > 0) {
        setSelectedTable(data.tables[0].table_name);
      }
      
      setLoadingTables(false);
    } catch (error) {
      console.error('Error loading tables:', error);
      setError(`Failed to load tables: ${error.message}`);
      setLoadingTables(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedTable || !query.trim()) {
      setError('Please select a table and enter a query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/analyze/columns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          table_name: selectedTable,
          requirement: query,
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Analysis result:', result);
      
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
      setError(`Analysis failed: ${error.message}. Make sure backend is running!`);
    } finally {
      setLoading(false);
    }
  };

  const totalColumns = tables.reduce((sum, table) => sum + (table.column_count || 0), 0);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 8 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600 }}>
          Welcome to Analytics Assistant! 🤖
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Ask questions about your data in plain English
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ 
            bgcolor: loadingTables ? '#f5f5f5' : tables.length > 0 ? '#e3f2fd' : '#ffebee',
            transition: 'all 0.3s'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <StorageIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    {loadingTables ? '...' : tables.length}
                  </Typography>
                  <Typography color="text.secondary" variant="body2">
                    Data Sources
                  </Typography>
                </Box>
              </Box>
              {!loadingTables && tables.length === 0 && (
                <Chip label="Backend not connected" color="error" size="small" />
              )}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DataObjectIcon sx={{ fontSize: 40, mr: 2, color: 'warning.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    {totalColumns}
                  </Typography>
                  <Typography color="text.secondary" variant="body2">
                    Total Columns
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BarChartIcon sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    0
                  </Typography>
                  <Typography color="text.secondary" variant="body2">
                    Reports Generated
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          {error}
          {error.includes('Backend') && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                Make sure the backend is running: 
                <code style={{ 
                  background: '#ffebee', 
                  padding: '2px 6px', 
                  borderRadius: '4px',
                  marginLeft: '8px'
                }}>
                  cd analytics-assistance && ./venv/bin/uvicorn app.main:app --reload
                </code>
              </Typography>
            </Box>
          )}
        </Alert>
      )}

      {/* Backend Connection Status */}
      {loadingTables && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <CircularProgress size={20} sx={{ mr: 2 }} />
          Connecting to backend...
        </Alert>
      )}

      {!loadingTables && tables.length === 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <AlertTitle>No Tables Found</AlertTitle>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Backend is running but no tables are available. Check if:
          </Typography>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>Database file exists: <code>analytics-assistance/data/analytics.db</code></li>
            <li>Tables were loaded using the SQL scripts</li>
            <li>Schema registry is working correctly</li>
          </ul>
          <Button 
            size="small" 
            onClick={loadTables} 
            sx={{ mt: 1 }}
            variant="outlined"
          >
            🔄 Retry Connection
          </Button>
        </Alert>
      )}

      {/* Main Query Section */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          bgcolor: '#f8f9fa',
          borderRadius: 3,
          border: '2px solid #e0e0e0'
        }}
      >
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <SearchIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            💬 Ask Anything About Your Data
          </Typography>
          <Typography color="text.secondary">
            Select a table, type your question, and let AI do the rest!
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Table Selector */}
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              label="📊 Select Data Source"
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              disabled={loadingTables || tables.length === 0}
              variant="outlined"
              sx={{ 
                bgcolor: 'white',
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            >
              {loadingTables ? (
                <MenuItem disabled>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Loading tables...
                </MenuItem>
              ) : tables.length === 0 ? (
                <MenuItem disabled>No tables available</MenuItem>
              ) : (
                tables.map((table) => (
                  <MenuItem key={table.table_name} value={table.table_name}>
                    <Box>
                      <Typography variant="body1">{table.table_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {table.column_count} columns
                      </Typography>
                    </Box>
                  </MenuItem>
                ))
              )}
            </TextField>
          </Grid>

          {/* Query Input */}
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="✍️ Your Question"
              placeholder='e.g., "Show me average MRR by industry for enterprise customers"'
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleAnalyze();
                }
              }}
              variant="outlined"
              sx={{ 
                bgcolor: 'white',
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
              helperText="Press Enter to analyze, Shift+Enter for new line"
            />
          </Grid>

          {/* Analyze Button */}
          <Grid item xs={12}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleAnalyze}
              disabled={loading || !selectedTable || !query.trim() || loadingTables}
              sx={{ 
                py: 2,
                fontSize: '1.1rem',
                fontWeight: 600,
                textTransform: 'none',
              }}
            >
              {loading ? (
                <>
                  <CircularProgress size={24} sx={{ mr: 2 }} color="inherit" />
                  Analyzing...
                </>
              ) : (
                <>
                  🚀 Analyze Query
                </>
              )}
            </Button>
          </Grid>
        </Grid>

        {/* Quick Examples */}
        {!loading && tables.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              💡 Try these examples:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {[
                "Show me average MRR by industry",
                "Count customers by country",
                "List top 10 customers by revenue",
                "Total sales by vendor"
              ].map((example, index) => (
                <Chip
                  key={index}
                  label={example}
                  onClick={() => setQuery(example)}
                  sx={{ cursor: 'pointer' }}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Recent Reports Section */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
          📈 Recent Reports
        </Typography>
        <Paper sx={{ p: 3, textAlign: 'center', bgcolor: '#fafafa' }}>
          <Typography color="text.secondary">
            Your recent reports will appear here...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Generate your first report to get started!
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}

export default HomePage;
