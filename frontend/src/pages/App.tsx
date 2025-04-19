import React from 'react';
import { CssBaseline, Container, Typography } from '@mui/material';
import MapView from '../components/MapView';

const App: React.FC = () => {
  return (
    <>
      <CssBaseline />
      <Container maxWidth="xl" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          OrataMap: Spatial Data Manager
        </Typography>
        <div style={{ flex: 1, minHeight: 0 }}>
          <MapView />
        </div>
      </Container>
    </>
  );
};

export default App;
