import React from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, CircularProgress } from '@mui/material';

interface ImportDialogProps {
  open: boolean;
  fileToUpload: File | null;
  uploadStatus: 'idle' | 'uploading' | 'success' | 'error';
  uploadError: string | null;
  onFileChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onClose: () => void;
  onUpload: () => void;
}

/**
 * Dialog for importing a GeoPackage file and uploading it to the backend.
 */
const ImportDialog: React.FC<ImportDialogProps> = ({
  open,
  fileToUpload,
  uploadStatus,
  uploadError,
  onFileChange,
  onClose,
  onUpload
}) => (
  <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
    <DialogTitle>Import GeoPackage File</DialogTitle>
    <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '10px !important' }}>
      {/* Simple File Input */}
      <Button component="label" variant="outlined" disabled={uploadStatus === 'uploading'}>
        Select .gpkg File
        <input 
          type="file" 
          accept=".gpkg"
          hidden
          onChange={onFileChange}
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
      <Button onClick={onClose} disabled={uploadStatus === 'uploading'}>Cancel</Button>
      <Button onClick={onUpload} disabled={!fileToUpload || uploadStatus === 'uploading'} variant="contained">Import</Button>
    </DialogActions>
  </Dialog>
);

export default ImportDialog;
