import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import TuneIcon from '@mui/icons-material/Tune'; // Buffer tool icon


interface ToolbarProps {
  onImportClick: () => void;
  onBufferClick: () => void;
}

/**
 * App toolbar for spatial/map functions.
 * Add more buttons as needed for future tools.
 *
 * Props:
 *   onImportClick: Called when the import button is clicked.
 *   onBufferClick: Called when the buffer tool button is clicked.
 */
const Toolbar: React.FC<ToolbarProps> = ({ onImportClick, onBufferClick }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: 1,
        p: 1,
        bgcolor: 'background.paper',
        borderRadius: 1,
        boxShadow: 2,
        position: 'absolute',
        top: 16,
        left: 16,
        zIndex: 1200,
      }}
    >
      <Tooltip title="Buffer Tool">
        <IconButton color="secondary" onClick={onBufferClick} size="large">
          <TuneIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Import GeoPackage">
        <IconButton color="primary" onClick={onImportClick} size="large">
          <CloudUploadIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

export default Toolbar;
