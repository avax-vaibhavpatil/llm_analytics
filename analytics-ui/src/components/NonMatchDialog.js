/**
 * NonMatchDialog Component
 * 
 * This dialog shows when AI cannot find all required columns.
 * User can either:
 * 1. Edit their query and try again
 * 2. Register the query with admin for review
 * 
 * Props:
 * - open: boolean - Show/hide dialog
 * - onClose: function - Called when dialog should close
 * - query: string - Original user query
 * - result: object - Analysis result with missing columns
 * - table: string - Table name
 * - onEditQuery: function - Called when user wants to edit query
 * - onRegisterAdmin: function - Called when user wants to register with admin
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  Divider,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Send as SendIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

function NonMatchDialog({ 
  open, 
  onClose, 
  query, 
  result, 
  table,
  onEditQuery, 
  onRegisterAdmin 
}) {
  // If no result data, don't render anything
  if (!result) {
    return null;
  }

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"  // Medium width
      fullWidth       // Take full width up to maxWidth
    >
      {/* ═══════════════════════════════════════════════════════════
          DIALOG TITLE
          ═══════════════════════════════════════════════════════════ */}
      <DialogTitle sx={{ 
        bgcolor: '#fff3e0',  // Light orange background
        color: '#e65100',     // Dark orange text
        display: 'flex',
        alignItems: 'center',
        gap: 1
      }}>
        <WarningIcon />
        Required Data Field Not Available
      </DialogTitle>

      {/* ═══════════════════════════════════════════════════════════
          DIALOG CONTENT
          ═══════════════════════════════════════════════════════════ */}
      <DialogContent sx={{ mt: 2 }}>
        
        {/* Alert Message */}
        <Alert severity="warning" sx={{ mb: 3 }}>
          The system could not find all required data fields for your query.
          You can either modify your query or register it with admin for review.
        </Alert>

        {/* User's Original Query */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            📝 Your Original Query:
          </Typography>
          <Box sx={{ 
            p: 2, 
            bgcolor: '#f5f5f5', 
            borderRadius: 1,
            border: '1px solid #e0e0e0'
          }}>
            <Typography variant="body1">
              "{query}"
            </Typography>
          </Box>
        </Box>

        {/* Table Name */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            📊 Table:
          </Typography>
          <Chip 
            label={table} 
            color="primary" 
            variant="outlined"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Technical Interpretation */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            💡 Query's Technical Interpretation:
          </Typography>
          <Box sx={{ 
            p: 2, 
            bgcolor: '#e3f2fd',  // Light blue background
            borderRadius: 1,
            border: '1px solid #90caf9'
          }}>
            <Typography variant="body2">
              {result.technical_summary}
            </Typography>
          </Box>
        </Box>

        {/* Missing Columns */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="error" gutterBottom>
            ❌ Missing Columns:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {result.missing_columns && result.missing_columns.length > 0 ? (
              result.missing_columns.map((column) => (
                <Chip 
                  key={column}
                  label={column}
                  color="error"
                  size="small"
                />
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                None
              </Typography>
            )}
          </Box>
        </Box>

        {/* Available Columns (if any) */}
        {result.available_columns && result.available_columns.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="success.main" gutterBottom>
              ✅ Available Columns:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {result.available_columns.map((column) => (
                <Chip 
                  key={column}
                  label={column}
                  color="success"
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Required Columns */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
            📋 Required Columns:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {result.required_columns && result.required_columns.length > 0 ? (
              result.required_columns.map((column) => (
                <Chip 
                  key={column}
                  label={column}
                  color="primary"
                  size="small"
                  variant="outlined"
                />
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                None
              </Typography>
            )}
          </Box>
        </Box>

      </DialogContent>

      {/* ═══════════════════════════════════════════════════════════
          DIALOG ACTIONS (Buttons)
          ═══════════════════════════════════════════════════════════ */}
      <DialogActions sx={{ p: 2, bgcolor: '#fafafa' }}>
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          width: '100%',
          justifyContent: 'space-between'
        }}>
          
          {/* Edit Query Button */}
          <Button
            variant="outlined"
            color="primary"
            startIcon={<EditIcon />}
            onClick={onEditQuery}
            size="large"
          >
            Edit Query
          </Button>

          {/* Register with Admin Button */}
          <Button
            variant="contained"
            color="warning"
            startIcon={<SendIcon />}
            onClick={onRegisterAdmin}
            size="large"
          >
            Register with Admin
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

export default NonMatchDialog;

/**
 * EXPLANATION:
 * 
 * 1. Props (Component Inputs):
 *    - open: Controls if dialog is visible
 *    - query: User's original text query
 *    - result: Contains technical_summary, missing_columns, etc.
 *    - onEditQuery: Function to call when "Edit Query" clicked
 *    - onRegisterAdmin: Function to call when "Register" clicked
 * 
 * 2. Material-UI Components Used:
 *    - Dialog: Modal popup that blocks background
 *    - DialogTitle: Header area with title
 *    - DialogContent: Main content area
 *    - DialogActions: Footer area with buttons
 *    - Box: Container for layout (like <div>)
 *    - Typography: Text with consistent styling
 *    - Chip: Small label/tag component
 *    - Alert: Colored message box
 * 
 * 3. Styling with sx prop:
 *    - sx={{ mb: 3 }} = margin-bottom: 3 * 8px = 24px
 *    - sx={{ p: 2 }} = padding: 2 * 8px = 16px
 *    - bgcolor = background color
 *    - borderRadius = rounded corners
 * 
 * 4. Conditional Rendering:
 *    - {condition && <Component />} = Only show if condition is true
 *    - {array.map(...)} = Loop through array and render each item
 * 
 * 5. Event Handlers:
 *    - onClick={onEditQuery} = Call function when button clicked
 *    - Parent component decides what happens
 * 
 * NEXT: We'll use this component in AvailabilityPage!
 */

