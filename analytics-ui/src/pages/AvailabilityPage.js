import React from 'react';
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
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  ArrowForward as ArrowIcon,
  Email as EmailIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';

function AvailabilityPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data from previous screen
  const { result, query, table } = location.state || {};

  // If no data, redirect to home
  if (!result) {
    navigate('/');
    return null;
  }

  // Determine status
  const allAvailable = result.missing_columns.length === 0;
  const partiallyAvailable = result.available_columns.length > 0 && result.missing_columns.length > 0;
  const nothingAvailable = result.available_columns.length === 0;

  // Handle "Proceed to Report" button
  const handleProceed = () => {
    navigate('/preview', { state: { result, query, table } });
  };

  // Handle "Modify Query" button
  const handleModify = () => {
    navigate('/');
  };

  // Handle "Request from Admin" button
  const handleRequestAdmin = () => {
    alert(`📧 Request sent to admin for missing columns: ${result.missing_columns.join(', ')}`);
    // In real app, this would send email/notification
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
                    onClick={handleRequestAdmin}
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
        </Container>
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


