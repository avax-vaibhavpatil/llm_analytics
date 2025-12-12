import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Alert,
  Chip,
  Divider,
  Grid,
  TextField,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowIcon,
  Email as EmailIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';
import NonMatchDialog from '../components/NonMatchDialog';
import { registerAdminRequest, analyzeColumns } from '../services/api';

function AvailabilityPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data from previous screen
  const { result, query, table } = location.state || {};

  // ═══════════════════════════════════════════════════════════
  // STATE MANAGEMENT
  // ═══════════════════════════════════════════════════════════
  
  // Dialog state
  const [showDialog, setShowDialog] = useState(false);
  
  // Edit mode state
  const [editMode, setEditMode] = useState(false);
  const [editedQuery, setEditedQuery] = useState(query || '');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // If no data, redirect to home
  if (!result) {
    navigate('/');
    return null;
  }

  // Determine status
  const allAvailable = result.missing_columns.length === 0;
  const partiallyAvailable = result.available_columns.length > 0 && result.missing_columns.length > 0;
  const nothingAvailable = result.available_columns.length === 0;

  // ═══════════════════════════════════════════════════════════
  // EFFECT: Show dialog when missing columns detected
  // ═══════════════════════════════════════════════════════════
  
  useEffect(() => {
    // Automatically show dialog if there are missing columns
    if (result.missing_columns && result.missing_columns.length > 0) {
      setShowDialog(true);
    }
  }, [result.missing_columns]);

  // ═══════════════════════════════════════════════════════════
  // EVENT HANDLERS
  // ═══════════════════════════════════════════════════════════

  // Handle "Proceed to Report" button
  const handleProceed = () => {
    navigate('/preview', { state: { result, query, table } });
  };

  // Handle "Modify Query" button
  const handleModify = () => {
    navigate('/');
  };

  // Handle "Edit Query" from dialog
  const handleEditQuery = () => {
    setShowDialog(false);
    setEditMode(true);
    setEditedQuery(query);
  };

  // Handle re-analyzing edited query
  const handleReanalyze = async () => {
    if (!editedQuery.trim()) {
      alert('Please enter a query');
      return;
    }

    setIsAnalyzing(true);

    try {
      // Call API to analyze the new query
      const newResult = await analyzeColumns(table, editedQuery);
      
      // Check if still has missing columns
      if (newResult.missing_columns && newResult.missing_columns.length > 0) {
        // Still missing columns - show dialog again
        setShowDialog(true);
        setEditMode(false);
        
        // Update the location state with new result
        navigate('/availability', {
          state: { result: newResult, query: editedQuery, table },
          replace: true
        });
      } else {
        // All columns found! Proceed to preview
        navigate('/preview', {
          state: { result: newResult, query: editedQuery, table }
        });
      }
    } catch (error) {
      alert(`Error analyzing query: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle "Register with Admin" from dialog
  const handleRegisterAdmin = async () => {
    setShowDialog(false);

    try {
      // Call API to register the query with admin
      const response = await registerAdminRequest({
        original_query: query,
        technical_interpretation: result.technical_summary,
        table_name: table,
        required_columns: result.required_columns,
        missing_columns: result.missing_columns,
        available_columns: result.available_columns,
      });

      // Show success message
      alert(`✅ ${response.message}\n\nRequest ID: ${response.request_id}`);
      
      // Redirect to home
      navigate('/');
    } catch (error) {
      alert(`❌ Failed to register query: ${error.message}`);
    }
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
        <Container maxWidth="md" sx={{ mt: 4 }}>
          {/* Header with Status */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            {allAvailable && (
              <>
                <Typography variant="h4" color="success.main" gutterBottom>
                  ✅ Great News! All Data is Available
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  All required columns exist in the table. You can proceed with the report.
                </Typography>
              </>
            )}
            
            {partiallyAvailable && (
              <>
                <Typography variant="h4" color="warning.main" gutterBottom>
                  ⚠️ Some Data is Missing
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Some columns are available, but others are missing.
                </Typography>
              </>
            )}
            
            {nothingAvailable && (
              <>
                <Typography variant="h4" color="error.main" gutterBottom>
                  ❌ Required Data Not Available
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  None of the required columns exist in this table.
                </Typography>
              </>
            )}
          </Box>

          {/* Main Card */}
          <Paper elevation={3} sx={{ p: 4 }}>
            {/* Query Summary */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary">
                Your Request:
              </Typography>
              <Typography variant="body1" sx={{ fontStyle: 'italic', mt: 1 }}>
                "{query}"
              </Typography>
              <Chip 
                label={`Table: ${table}`} 
                size="small" 
                sx={{ mt: 1 }} 
              />
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Technical Summary */}
            <Box sx={{ mb: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                💡 What we understood:
              </Typography>
              <Typography variant="body2">
                {result.technical_summary}
              </Typography>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Available Columns */}
            {result.available_columns.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" color="success.main" gutterBottom>
                  ✅ Available Columns ({result.available_columns.length})
                </Typography>
                <Paper variant="outlined" sx={{ bgcolor: '#f1f8f4' }}>
                  <List>
                    {result.available_columns.map((column) => (
                      <ListItem key={column}>
                        <ListItemIcon>
                          <CheckIcon color="success" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={column}
                          secondary="Ready to use"
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}

            {/* Missing Columns */}
            {result.missing_columns.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" color="error.main" gutterBottom>
                  ❌ Missing Columns ({result.missing_columns.length})
                </Typography>
                <Paper variant="outlined" sx={{ bgcolor: '#fff4f4' }}>
                  <List>
                    {result.missing_columns.map((column) => (
                      <ListItem key={column}>
                        <ListItemIcon>
                          <CancelIcon color="error" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={column}
                          secondary="Not found in table"
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}

            {/* Optional Columns */}
            {result.optional_columns && result.optional_columns.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" color="info.main" gutterBottom>
                  💡 Optional Columns (Would enhance analysis)
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {result.optional_columns.join(', ')}
                </Typography>
              </Box>
            )}

            <Divider sx={{ my: 3 }} />

            {/* Recommendations */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                🎯 Recommendations:
              </Typography>
              {result.recommendations.map((rec, index) => (
                <Alert 
                  key={index} 
                  severity={
                    rec.includes('✅') ? 'success' : 
                    rec.includes('⚠️') ? 'warning' : 
                    'info'
                  }
                  sx={{ mb: 1 }}
                >
                  {rec}
                </Alert>
              ))}
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Action Buttons */}
            <Grid container spacing={2}>
              {/* Proceed Button (if all or partial data available) */}
              {result.available_columns.length > 0 && (
                <Grid item xs={12} sm={6}>
                  <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    size="large"
                    endIcon={<ArrowIcon />}
                    onClick={handleProceed}
                  >
                    {allAvailable ? 'Proceed to Report Preview' : 'Proceed with Available Data'}
                  </Button>
                </Grid>
              )}

              {/* Request Admin Button (if missing columns) */}
              {result.missing_columns.length > 0 && (
                <Grid item xs={12} sm={result.available_columns.length > 0 ? 6 : 12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    color="warning"
                    size="large"
                    startIcon={<EmailIcon />}
                    onClick={() => setShowDialog(true)}
                  >
                    Request Missing Columns from Admin
                  </Button>
                </Grid>
              )}

              {/* Modify Query Button */}
              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="text"
                  startIcon={<EditIcon />}
                  onClick={handleModify}
                >
                  Modify Query
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {/* ═══════════════════════════════════════════════════════════
              EDIT MODE - Query Editor
              ═══════════════════════════════════════════════════════════ */}
          {editMode && (
            <Paper elevation={3} sx={{ p: 4, mt: 3, bgcolor: '#fff9e6' }}>
              <Typography variant="h6" gutterBottom>
                ✏️ Edit Your Query
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Modify your query to better match available columns, then re-analyze.
              </Typography>
              
              <TextField
                fullWidth
                multiline
                rows={3}
                value={editedQuery}
                onChange={(e) => setEditedQuery(e.target.value)}
                placeholder="Enter your modified query..."
                variant="outlined"
                sx={{ mb: 2 }}
              />
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleReanalyze}
                  disabled={isAnalyzing}
                  startIcon={isAnalyzing ? <CircularProgress size={20} /> : null}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Re-analyze Query'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setEditMode(false)}
                  disabled={isAnalyzing}
                >
                  Cancel
                </Button>
              </Box>
            </Paper>
          )}
        </Container>

        {/* ═══════════════════════════════════════════════════════════
            NON-MATCH DIALOG
            ═══════════════════════════════════════════════════════════ */}
        <NonMatchDialog
          open={showDialog}
          onClose={() => setShowDialog(false)}
          query={query}
          result={result}
          table={table}
          onEditQuery={handleEditQuery}
          onRegisterAdmin={handleRegisterAdmin}
        />
      </Box>
    </Box>
  );
}

export default AvailabilityPage;

/*
 * EXPLANATION:
 * 
 * KEY FEATURES:
 * 
 * 1. Dynamic Status Header:
 *    - Green (✅) if all available
 *    - Yellow (⚠️) if partially available
 *    - Red (❌) if nothing available
 * 
 * 2. Available Columns List:
 *    - Green background (#f1f8f4)
 *    - CheckIcon for each column
 *    - Shows "Ready to use"
 * 
 * 3. Missing Columns List:
 *    - Red background (#fff4f4)
 *    - CancelIcon for each column
 *    - Shows "Not found in table"
 * 
 * 4. Smart Recommendations:
 *    - Different severity based on content
 *    - Auto-detects ✅, ⚠️ in text
 *    - Shows as colored alerts
 * 
 * 5. Conditional Buttons:
 *    - Proceed button: Shows if ANY columns available
 *    - Request Admin: Shows if ANY missing
 *    - Modify Query: Always available
 *    - Button text changes based on status
 * 
 * NEXT: Update App.js to add /availability route!
 */


