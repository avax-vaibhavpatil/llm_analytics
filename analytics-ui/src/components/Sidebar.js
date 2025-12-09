import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
} from '@mui/material';
import {
  Home as HomeIcon,
  AddCircle as AddIcon,
  History as HistoryIcon,
  Storage as StorageIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const drawerWidth = 240;

function Sidebar() {
  const navigate = useNavigate();

  // Menu items
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Create Report', icon: <AddIcon />, path: '/create' },
    { text: 'History', icon: <HistoryIcon />, path: '/history' },
    { text: 'Data Warehouse', icon: <StorageIcon />, path: '/warehouse' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      {/* App Title */}
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Analytics Assistant
        </Typography>
      </Toolbar>
      
      <Divider />
      
      {/* Menu Items */}
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => navigate(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider />
      
      {/* Settings at bottom */}
      <List sx={{ marginTop: 'auto' }}>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate('/settings')}>
            <ListItemIcon><SettingsIcon /></ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Drawer>
  );
}

export default Sidebar;

/*
 * EXPLANATION:
 * 
 * 1. Drawer: Material-UI's sidebar component
 * 2. variant="permanent": Always visible (not hidden)
 * 3. menuItems: Array of menu options
 * 4. navigate(): Function to change pages
 * 5. Icons: Visual indicators for each menu item
 * 
 * This sidebar will be visible on ALL pages!
 */


