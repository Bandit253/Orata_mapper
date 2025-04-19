import React, { useEffect, useRef, useState, DragEvent, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import Toolbar from './Toolbar';
import 'maplibre-gl/dist/maplibre-gl.css';
import {
  FormControl, InputLabel, MenuItem, Select, SelectChangeEvent, Box, Paper, Typography, List, ListItem, ListItemText, IconButton, CircularProgress,
  Button, Dialog, DialogActions, DialogContent, DialogTitle
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import DeleteIcon from '@mui/icons-material/Delete';
import Menu from '@mui/material/Menu';
import axios from 'axios';

const OSM_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: [
        'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: ' OpenStreetMap contributors',
    },
  },
  layers: [
    {
      id: 'osm',
      type: 'raster',
      source: 'osm',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

const GOOGLE_SATELLITE_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    satellite: {
      type: 'raster',
      tiles: [
        'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
      ],
      tileSize: 256,
      attribution: ' Google',
    },
  },
  layers: [
    {
      id: 'satellite',
      type: 'raster',
      source: 'satellite',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

const BASEMAP_OPTIONS = [
  { label: 'OpenStreetMap', value: 'osm', style: OSM_STYLE },
  { label: 'Google Satellite', value: 'satellite', style: GOOGLE_SATELLITE_STYLE },
];

const MELBOURNE_CENTER: [number, number] = [144.9631, -37.8136];

interface LayerEntry {
  tableName: string;
  visible: boolean;
  loading: boolean;
  error?: string;
}

const MapView: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [basemap, setBasemap] = useState('osm');
  const [layers, setLayers] = useState<LayerEntry[]>([]);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    tableName: string | null;
  } | null>(null);

  // Remove layer from map and TOC (frontend only)
  const handleRemoveLayer = (tableName: string) => {
    setLayers((prevLayers) => prevLayers.filter((layer) => layer.tableName !== tableName));
    // Remove layer from map if visible
    if (mapRef.current) {
      const map = mapRef.current;
      if (map.getSource(tableName)) {
        map.removeLayer(tableName);
        map.removeSource(tableName);
      }
    }
    handleCloseContextMenu();
  };

  // Toggle visibility and close menu
  const handleContextToggleVisibility = (tableName: string) => {
    handleLayerToggle(tableName);
    handleCloseContextMenu();
  };

  // Context menu handlers
  const handleContextMenu = (event: React.MouseEvent, tableName: string) => {
    event.preventDefault();
    setContextMenu(
      contextMenu === null
        ? {
            mouseX: event.clientX - 2,
            mouseY: event.clientY - 4,
            tableName,
          }
        : null,
    );
  };
  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  // Fetch existing tables on mount
  useEffect(() => {
    const fetchExistingTables = async () => {
      try {
        const response = await axios.get('/spatial-tables/');
        if (response.data && Array.isArray(response.data.tables)) {
          const existingLayers: LayerEntry[] = response.data.tables.map((tableName: string) => ({
            tableName,
            visible: false, // Start hidden
            loading: false,
            error: undefined,
          }));
          setLayers(existingLayers);
        }
      } catch (error) {
        console.error("Error fetching existing tables:", error);
        // Optionally show an error message to the user
      }
    };

    fetchExistingTables();
  }, []); // Empty dependency array ensures this runs only once on mount

  // Map initialization
  useEffect(() => {
    if (mapContainer.current && !mapRef.current) {
      mapRef.current = new maplibregl.Map({
        container: mapContainer.current,
        style: OSM_STYLE,
        center: MELBOURNE_CENTER,
        zoom: 10,
      });
    }
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  // Basemap switching
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setStyle(
        basemap === 'osm' ? OSM_STYLE : GOOGLE_SATELLITE_STYLE
      );
      // Re-add all visible layers after style change
      layers.forEach(layer => {
        if (layer.visible) {
          fetchAndShowLayer(layer.tableName);
        }
      });
    }
  }, [basemap]);

  // Helper: Fetch features for a table within current bbox (+5%) and add to map
  const fetchAndShowLayer = async (tableName: string) => {
    if (!mapRef.current) return;
    const map = mapRef.current;
    const bounds = map.getBounds();
    const expand = (min: number, max: number, pct: number) => {
      const center = (min + max) / 2;
      const half = (max - min) / 2 * (1 + pct);
      return [center - half, center + half];
    };
    const [minLng, maxLng] = expand(bounds.getWest(), bounds.getEast(), 0.05);
    const [minLat, maxLat] = expand(bounds.getSouth(), bounds.getNorth(), 0.05);
    try {
      const resp = await axios.post(`/features/${tableName}/query/bbox`, {
        bbox: [minLng, minLat, maxLng, maxLat],
      });
      const geojson = resp.data;
      // Remove existing source/layer if present
      if (map.getSource(tableName)) {
        map.removeLayer(tableName);
        map.removeSource(tableName);
      }
      map.addSource(tableName, {
        type: 'geojson',
        data: geojson,
      });
      map.addLayer({
        id: tableName,
        type: 'circle',
        source: tableName,
        paint: {
          'circle-radius': 6,
          'circle-color': '#1976d2',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff',
        },
      });
    } catch (err) {
      console.error("Failed to fetch features for", tableName, err); // Log error
      setLayers(currentLayers => currentLayers.map(l => l.tableName === tableName ? { ...l, error: 'Failed to fetch features' } : l));
    }
  };

  // TOC Layer toggle
  const handleLayerToggle = (tableName: string) => {
    setLayers(layers => layers.map(l =>
      l.tableName === tableName ? { ...l, visible: !l.visible } : l
    ));
    if (mapRef.current) {
      if (mapRef.current.getLayer(tableName)) {
        if (mapRef.current.getLayoutProperty(tableName, 'visibility') === 'none') {
          mapRef.current.setLayoutProperty(tableName, 'visibility', 'visible');
        } else {
          mapRef.current.setLayoutProperty(tableName, 'visibility', 'none');
        }
      } else {
        fetchAndShowLayer(tableName);
      }
    }
  };

  const handleImportDialogOpen = () => {
    setImportDialogOpen(true);
  };

  const handleImportDialogClose = () => {
    setImportDialogOpen(false);
    // Reset state on close
    setFileToUpload(null);
    setUploadStatus('idle');
    setUploadError(null);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      if (file.name.toLowerCase().endsWith('.gpkg')) {
        setFileToUpload(file);
        setUploadStatus('idle'); // Reset status if a new file is selected
        setUploadError(null);
      } else {
        alert('Only .gpkg files are supported.');
        setFileToUpload(null); // Clear invalid file
        event.target.value = ''; // Reset input field
      }
    } else {
      setFileToUpload(null);
    }
  };

  // Renamed from old handleDrop logic
  const handleUpload = async () => {
    if (!fileToUpload) return;

    const tableName = fileToUpload.name.replace(/\.gpkg$/i, '');
    // Add layer entry with loading state immediately
    setLayers(currentLayers => [
      ...currentLayers.filter(l => l.tableName !== tableName),
      { tableName, visible: false, loading: true, error: undefined }
    ]);

    setUploadStatus('uploading');
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', fileToUpload);
      await axios.post('/import/geopackage/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      // Success: Update layer status (remove loading), fetch data, update dialog
      setLayers(currentLayers => currentLayers.map(l => 
        l.tableName === tableName ? { ...l, loading: false, visible: true } : l
      ));
      fetchAndShowLayer(tableName); // Fetch data for the newly added layer
      setUploadStatus('success');
    } catch (err: any) {
      // Error: Update layer status (remove loading, add error), update dialog
      const errorMsg = err?.response?.data?.detail || err?.message || 'Import failed';
      setLayers(currentLayers => currentLayers.map(l => 
        l.tableName === tableName ? { ...l, loading: false, error: errorMsg } : l
      ));
      setUploadStatus('error');
      setUploadError(errorMsg);
    }
  };

  return (
    <Box sx={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'row' }}>
      {/* Sidebar for controls */}
      <Box sx={{ width: 340, minWidth: 280, maxWidth: 400, height: '100%', bgcolor: 'background.paper', boxShadow: 2, zIndex: 1200, display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
        {/* Toolbar */}
        <Toolbar onImportClick={handleImportDialogOpen} />
        {/* Basemap Selector */}
        <Box sx={{ mb: 2 }}>
          <FormControl size="small" fullWidth>
            <InputLabel id="basemap-select-label">Basemap</InputLabel>
            <Select
              labelId="basemap-select-label"
              id="basemap-select"
              value={basemap}
              onChange={(e: SelectChangeEvent) => setBasemap(e.target.value)}
            >
              {BASEMAP_OPTIONS.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
        {/* TOC */}
        <Paper
          elevation={1}
          sx={{ flex: 1, overflowY: 'auto', p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            Table of Contents
          </Typography>
          <List>
            {layers.map(layer => (
              <ListItem
                key={layer.tableName}
                onContextMenu={e => handleContextMenu(e, layer.tableName)}
                sx={{
                  opacity: layer.visible ? 1 : 0.5,
                  cursor: 'context-menu',
                  userSelect: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <ListItemText
                  primary={layer.tableName}
                  primaryTypographyProps={{
                    color: layer.visible ? 'text.primary' : 'text.secondary',
                    fontWeight: layer.visible ? 500 : 400,
                  }}
                />
                <IconButton
                  edge="end"
                  onClick={e => {
                    e.stopPropagation();
                    handleLayerToggle(layer.tableName);
                  }}
                  title={layer.visible ? 'Hide Layer' : 'Show Layer'}
                >
                  {layer.visible ? <VisibilityIcon /> : <VisibilityOffIcon />}
                </IconButton>
              </ListItem>
            ))}
          </List>
          {/* Context Menu for layers */}
          <Menu
            open={contextMenu !== null}
            onClose={handleCloseContextMenu}
            anchorReference="anchorPosition"
            anchorPosition={
              contextMenu !== null
                ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
                : undefined
            }
            MenuListProps={{ 'aria-labelledby': 'layer-context-menu' }}
          >
            <MenuItem
              onClick={() => contextMenu && handleContextToggleVisibility(contextMenu.tableName!)}
              disabled={!contextMenu}
            >
              {contextMenu && layers.find(l => l.tableName === contextMenu.tableName)?.visible
                ? 'Hide Layer'
                : 'Show Layer'}
            </MenuItem>
            <MenuItem
              onClick={() => contextMenu && handleRemoveLayer(contextMenu.tableName!)}
              disabled={!contextMenu}
            >
              Remove from Map
            </MenuItem>
          </Menu>
        </Paper>
      </Box>
      {/* Map Canvas fills the rest of the space */}
      <Box sx={{ flex: 1, height: '100%', position: 'relative' }}>
        <div
          ref={mapContainer}
          style={{ width: '100%', height: '100%' }}
        />
        <Dialog open={importDialogOpen} onClose={handleImportDialogClose} maxWidth="sm" fullWidth>
          <DialogTitle>Import GeoPackage File</DialogTitle>
          <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '10px !important' }}>
            {/* Simple File Input */}
            <Button component="label" variant="outlined" disabled={uploadStatus === 'uploading'}>
              Select .gpkg File
              <input 
                type="file" 
                accept=".gpkg"
                hidden
                onChange={handleFileChange}
              />
            </Button>
            {fileToUpload && (
              <Typography variant="body2">Selected: {fileToUpload.name}</Typography>
            )}
            {uploadStatus === 'uploading' && <CircularProgress size={24} sx={{ alignSelf: 'center' }} />}
            {uploadStatus === 'error' && (
              <Typography color="error">{uploadError}</Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleImportDialogClose} disabled={uploadStatus === 'uploading'}>Cancel</Button>
            <Button onClick={handleUpload} disabled={!fileToUpload || uploadStatus === 'uploading'} variant="contained">Import</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Box>
  );
};

export default MapView;
