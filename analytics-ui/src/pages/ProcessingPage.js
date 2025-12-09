import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as PendingIcon,
} from '@mui/icons-material';
import Sidebar from '../components/Sidebar';

function ProcessingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get data passed from HomePage
  const { result, query, table } = location.state || {};
  
  // Processing steps animation
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    'Understanding requirement',
    'Identifying required columns',
    'Checking data availability',
    'Preparing results',
  ];

  useEffect(() => {
    // If no data, go back to home
    if (!result) {
      navigate('/');
      return;
    }

    // Animate through steps
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 500); // Each step takes 500ms

    // Update progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 100;
        return prev + 2;
      });
    }, 40);

    // Auto-redirect after 3 seconds
    const redirectTimer = setTimeout(() => {
      navigate('/availability', { state: { result, query, table } });
    }, 3000);

    // Cleanup
    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
      clearTimeout(redirectTimer);
    };
  }, [result, navigate]);

  if (!result) {
    return null;
  }

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
        <Container maxWidth="md" sx={{ mt: 8 }}>
          {/* Header */}
          <Typography variant="h4" align="center" gutterBottom>
            🤖 Analyzing Your Request
          </Typography>
          
          <Typography variant="body1" align="center" color="textSecondary" paragraph>
            Please wait while we process your analytics requirement...
          </Typography>

          {/* Main Processing Card */}
          <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
            {/* User's Query */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle2" color="textSecondary">
                Your Query:
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

            {/* Progress Steps */}
            <List sx={{ mb: 3 }}>
              {steps.map((step, index) => (
                <ListItem key={step}>
                  <ListItemIcon>
                    {index <= currentStep ? (
                      <CheckIcon color="success" />
                    ) : (
                      <PendingIcon color="disabled" />
                    )}
                  </ListItemIcon>
                  <ListItemText 
                    primary={step}
                    secondary={index <= currentStep ? 'Done' : 'Pending'}
                  />
                </ListItem>
              ))}
            </List>

            {/* Progress Bar */}
            <LinearProgress variant="determinate" value={progress} sx={{ mb: 3 }} />
            <Typography variant="body2" align="center" color="textSecondary">
              {Math.round(progress)}% complete
            </Typography>

            {/* Technical Interpretation (revealed after step 1) */}
            {currentStep >= 0 && (
              <Box sx={{ mt: 4, p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  💡 Technical Interpretation:
                </Typography>
                <Typography variant="body2">
                  {result.technical_summary}
                </Typography>
              </Box>
            )}

            {/* Required Columns (revealed after step 2) */}
            {currentStep >= 1 && (
              <Box sx={{ mt: 2, p: 2, bgcolor: '#e3f2fd', borderRadius: 2 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  📝 Required Columns:
                </Typography>
                <Typography variant="body2">
                  {result.required_columns.join(', ')}
                </Typography>
              </Box>
            )}
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}

export default ProcessingPage;

/*
 * EXPLANATION:
 * 
 * HOW IT WORKS:
 * 
 * 1. Receives Data:
 *    - location.state contains: result, query, table
 *    - Passed from HomePage when user clicks Analyze
 * 
 * 2. Step Animation:
 *    - setInterval updates currentStep every 500ms
 *    - Shows checkmarks as steps complete
 *    - Creates smooth progression feeling
 * 
 * 3. Progress Bar:
 *    - Updates every 40ms (0% → 100%)
 *    - Visual feedback for user
 * 
 * 4. Auto-redirect:
 *    - After 3 seconds, goes to Availability page
 *    - Passes the result data along
 * 
 * 5. Content Reveal:
 *    - Technical interpretation shows after step 1
 *    - Required columns show after step 2
 *    - Progressive disclosure keeps user engaged
 * 
 * NEXT: Update HomePage to navigate here instead of showing alert!
 */


