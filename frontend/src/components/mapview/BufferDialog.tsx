import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Typography, TextField, Button, CircularProgress } from '@mui/material';

interface BufferDialogProps {
  open: boolean;
  geometry: string;
  distance: number;
  loading: boolean;
  error: string | null;
  onGeometryChange: (val: string) => void;
  onDistanceChange: (val: number) => void;
  onClose: () => void;
  onSubmit: () => void;
}

/**
 * Dialog for entering geometry and buffer distance, and triggering buffer API call.
 */
const BufferDialog: React.FC<BufferDialogProps> = ({
  open,
  geometry,
  distance,
  loading,
  error,
  onGeometryChange,
  onDistanceChange,
  onClose,
  onSubmit
}) => (
  <Dialog open={open} onClose={onClose}>
    <DialogTitle>Buffer Tool</DialogTitle>
    <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 400 }}>
      <Typography variant="body2">
        Enter a GeoJSON geometry and buffer distance (meters):
      </Typography>
      <TextField
        label="Geometry (GeoJSON)"
        value={geometry}
        onChange={e => onGeometryChange(e.target.value)}
        multiline
        minRows={3}
        fullWidth
        placeholder='{"type": "Point", "coordinates": [144.9631, -37.8136]}'
      />
      <TextField
        label="Buffer Distance (meters)"
        type="number"
        value={distance}
        onChange={e => onDistanceChange(Number(e.target.value))}
        inputProps={{ min: 1 }}
        fullWidth
      />
      {error && <Typography color="error">{error}</Typography>}
      {loading && <CircularProgress size={24} sx={{ alignSelf: 'center' }} />}
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} disabled={loading}>Cancel</Button>
      <Button onClick={onSubmit} variant="contained" color="secondary" disabled={loading}>
        {loading ? 'Buffering...' : 'Run Buffer'}
      </Button>
    </DialogActions>
  </Dialog>
);

export default BufferDialog;
