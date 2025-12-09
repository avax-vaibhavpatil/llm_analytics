import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Pages (we'll create these one by one)
import HomePage from './pages/HomePage';
import ProcessingPage from './pages/ProcessingPage';
import AvailabilityPage from './pages/AvailabilityPage';
import PreviewPage from './pages/PreviewPage';
import ReportPage from './pages/ReportPage';

// Create a nice theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Blue
    },
    secondary: {
      main: '#dc004e', // Pink
    },
    success: {
      main: '#4caf50', // Green
    },
    error: {
      main: '#f44336', // Red
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Route for home page */}
          <Route path="/" element={<HomePage />} />
          
          {/* Processing page */}
          <Route path="/processing" element={<ProcessingPage />} />
          
          {/* Availability check page */}
          <Route path="/availability" element={<AvailabilityPage />} />
          
          {/* Preview & Edit page */}
          <Route path="/preview" element={<PreviewPage />} />
          
          {/* Final Report page */}
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;

/*
 * EXPLANATION:
 * 
 * 1. ThemeProvider: Gives our app a consistent look
 * 2. CssBaseline: Resets browser default styles
 * 3. Router: Enables navigation between pages
 * 4. Routes: Defines which page shows for each URL
 * 
 * Right now we only have HomePage, we'll add more screens later!
 */
