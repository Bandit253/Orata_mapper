import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import Toolbar from './Toolbar';
import BufferDialog from './mapview/BufferDialog';
import LayerList, { LayerEntry } from './mapview/LayerList';
import LayerSelector from './mapview/LayerSelector';
import ImportDialog from './mapview/ImportDialog';
import { fetchAndShowLayer } from './mapview/mapUtils';
import 'maplibre-gl/dist/maplibre-gl.css';
import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent, Box } from '@mui/material';
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

const MapView: React.FC = () => {
  // Map and layers refs/state must be declared before any hooks that use them
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [layers, setLayers] = useState<LayerEntry[]>([]);
  const [basemap, setBasemap] = useState('osm');

  // Buffer tool dialog state & handlers
  const [bufferDialogOpen, setBufferDialogOpen] = useState(false);
  const [bufferGeometry, setBufferGeometry] = useState<string>('');
  const [bufferDistance, setBufferDistance] = useState<number>(100);
  const [bufferLoading, setBufferLoading] = useState(false);
  const [bufferError, setBufferError] = useState<string | null>(null);

  // LayerSelector state: which DB layers are selected for display
  const [selectedDbLayers, setSelectedDbLayers] = useState<string[]>([]);

  /**
   * Sync map layers with selectedDbLayers from LayerSelector.
   * Adds new layers, sets visibility, and fetches features for visible layers.
   */
  useEffect(() => {
    setLayers(prevLayers => {
      // Add new layers and update visibility
      const updated: LayerEntry[] = [];
      const seen = new Set<string>();
      // Add or update all layers currently in selectedDbLayers
      selectedDbLayers.forEach(tableName => {
        const existing = prevLayers.find(l => l.tableName === tableName);
        if (existing) {
          updated.push({ ...existing, visible: true });
        } else {
          updated.push({ tableName, visible: true, loading: false });
        }
        seen.add(tableName);
      });
      // Add any layers that are not selected, set visible: false
      prevLayers.forEach(l => {
        if (!seen.has(l.tableName)) {
          updated.push({ ...l, visible: false });
        }
      });
      return updated;
    });
  }, [selectedDbLayers]);

  // Fetch and show any layers that just became visible
  useEffect(() => {
    if (!mapRef.current) return;
    layers.forEach(layer => {
      if (layer.visible && (!mapRef.current!.getSource(layer.tableName))) {
        fetchAndShowLayer(mapRef.current!, layer.tableName, setLayers);
      } else if (!layer.visible && mapRef.current!.getSource(layer.tableName)) {
        // Remove layer from map if it is now hidden
        mapRef.current!.removeLayer(layer.tableName);
        mapRef.current!.removeSource(layer.tableName);
      }
    });
  }, [layers, mapRef.current]);

  const handleBufferDialogOpen = () => {
    setBufferDialogOpen(true);
    setBufferGeometry('');
    setBufferDistance(100);
    setBufferError(null);
  };
  const handleBufferDialogClose = () => {
    setBufferDialogOpen(false);
    setBufferGeometry('');
    setBufferDistance(100);
    setBufferError(null);
  };
  const handleBufferSubmit = async () => {
    setBufferLoading(true);
    setBufferError(null);
    try {
      let geometryObj;
      try {
        geometryObj = JSON.parse(bufferGeometry);
      } catch (e) {
        setBufferError('Invalid GeoJSON');
        setBufferLoading(false);
        return;
      }
      const table = layers.find(l => l.visible)?.tableName;
      if (!table) {
        setBufferError('No visible layer to buffer');
        setBufferLoading(false);
        return;
      }
      const response = await axios.post(`/features/${table}/query/buffer`, {
        geometry: geometryObj,
        buffer: bufferDistance
      });
      if (response.data && mapRef.current) {
        const layerId = `${table}_buffer_${Date.now()}`;
        if (mapRef.current.getSource(layerId)) {
          mapRef.current.removeLayer(layerId);
          mapRef.current.removeSource(layerId);
        }
        mapRef.current.addSource(layerId, {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: response.data.map((f: any) => f.geometry) },
        });
        mapRef.current.addLayer({
          id: layerId,
          type: 'fill',
          source: layerId,
          paint: {
            'fill-color': '#ff9800',
            'fill-opacity': 0.4,
            'fill-outline-color': '#d84315',
          },
        });
      }
      setBufferLoading(false);
      setBufferDialogOpen(false);
    } catch (err: any) {
      setBufferError(err?.response?.data?.detail || err?.message || 'Buffer query failed');
      setBufferLoading(false);
    }
  };


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

  // Remove layer from map and TOC
  const handleRemoveLayer = (tableName: string) => {
    setLayers((prevLayers) => prevLayers.filter((layer) => layer.tableName !== tableName));
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
            visible: false,
            loading: false,
            error: undefined,
          }));
          setLayers(existingLayers);
        }
      } catch (error) {
        console.error('Error fetching existing tables:', error);
      }
    };
    fetchExistingTables();
  }, []);
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
          fetchAndShowLayer(mapRef.current!, layer.tableName, setLayers);
        }
      });
    }
  }, [basemap]);
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
        fetchAndShowLayer(mapRef.current, tableName, setLayers);
      }
    }
  };
  // Import dialog handlers
  const handleImportDialogOpen = () => setImportDialogOpen(true);
  const handleImportDialogClose = () => {
    setImportDialogOpen(false);
    setFileToUpload(null);
    setUploadStatus('idle');
    setUploadError(null);
  };
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      if (file.name.toLowerCase().endsWith('.gpkg')) {
        setFileToUpload(file);
        setUploadStatus('idle');
        setUploadError(null);
      } else {
        alert('Only .gpkg files are supported.');
        setFileToUpload(null);
        event.target.value = '';
      }
    } else {
      setFileToUpload(null);
    }
  };
  const handleUpload = async () => {
    if (!fileToUpload) return;
    const tableName = fileToUpload.name.replace(/\.gpkg$/i, '');
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
      setLayers(currentLayers => currentLayers.map(l =>
        l.tableName === tableName ? { ...l, loading: false, visible: true } : l
      ));
      fetchAndShowLayer(mapRef.current!, tableName, setLayers);
      setUploadStatus('success');
    } catch (err: any) {
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
        <Toolbar onImportClick={handleImportDialogOpen} onBufferClick={handleBufferDialogOpen} />
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
        {/* LayerSelector tool: allows user to select DB layers to show */}
        <LayerSelector
          selectedLayers={selectedDbLayers}
          onChange={setSelectedDbLayers}
        />
        {/* TOC - LayerList component */}
        <LayerList
          layers={layers}
          contextMenu={contextMenu}
          onContextMenu={handleContextMenu}
          onToggleVisibility={handleContextToggleVisibility}
          onRemoveLayer={handleRemoveLayer}
          onCloseContextMenu={handleCloseContextMenu}
        />
      </Box>
      {/* Map Canvas fills the rest of the space */}
      <Box sx={{ flex: 1, height: '100%', position: 'relative' }}>
        <div
          ref={mapContainer}
          style={{ width: '100%', height: '100%' }}
        />
        {/* Import Dialog */}
        <ImportDialog
          open={importDialogOpen}
          fileToUpload={fileToUpload}
          uploadStatus={uploadStatus}
          uploadError={uploadError}
          onFileChange={handleFileChange}
          onClose={handleImportDialogClose}
          onUpload={handleUpload}
        />
        {/* Buffer Tool Dialog */}
        <BufferDialog
          open={bufferDialogOpen}
          geometry={bufferGeometry}
          distance={bufferDistance}
          loading={bufferLoading}
          error={bufferError}
          onGeometryChange={setBufferGeometry}
          onDistanceChange={setBufferDistance}
          onClose={handleBufferDialogClose}
          onSubmit={handleBufferSubmit}
        />
      </Box>
    </Box>
  );
};

export default MapView;

/**
 * Buffer tool dialog logic and API integration added to MapView.
 * - handleBufferDialogOpen/Close: open/close dialog
 * - handleBufferSubmit: call backend and add buffer result as a layer
 *
 * LayerSelector tool is now integrated to allow users to select layers from the database.
 * When the selection changes, selectedDbLayers is updated and can be used to control which layers are loaded/displayed on the map.
 */
