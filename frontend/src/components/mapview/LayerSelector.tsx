import React, { useEffect, useState } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput, Button } from '@mui/material';
import axios from 'axios';

interface LayerSelectorProps {
  selectedLayers: string[];
  onChange: (selected: string[]) => void;
}

/**
 * LayerSelector: Multi-select dropdown for available spatial layers from the DB.
 * Fetches layer list from backend and allows user to select layers to show on the map.
 */
const LayerSelector: React.FC<LayerSelectorProps> = ({ selectedLayers, onChange }) => {
  const [availableLayers, setAvailableLayers] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    axios.get('/spatial-tables/')
      .then(res => {
        console.log('LayerSelector API response:', res);
        if (Array.isArray(res.data.tables) && res.data.tables.length > 0) {
          setAvailableLayers(res.data.tables);
          setError(null);
        } else {
          setAvailableLayers([]);
          setError('No layers found');
        }
      })
      .catch(e => {
        setError('Failed to fetch layers');
        setAvailableLayers([]);
        console.error('LayerSelector API error:', e);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Box sx={{ mb: 2 }}>
      <FormControl fullWidth size="small">
        <InputLabel id="layer-selector-label">Select Layers</InputLabel>
        <Select
          labelId="layer-selector-label"
          multiple
          value={selectedLayers}
          onChange={e => onChange(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
          input={<OutlinedInput label="Select Layers" />}
          renderValue={selected => (selected as string[]).join(', ')}
        >
          {availableLayers.map((layer) => (
            <MenuItem key={layer} value={layer}>
              <Checkbox checked={selectedLayers.indexOf(layer) > -1} />
              <ListItemText primary={layer} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {loading && <div>Loading layers...</div>}
      {!loading && error && availableLayers.length === 0 && (
        <div style={{ color: 'red' }}>{error}</div>
      )}
    </Box>
  );
};

export default LayerSelector;
