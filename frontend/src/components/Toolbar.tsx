import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface ToolbarProps {
  onImportClick: () => void;
}

/**
 * App toolbar for spatial/map functions.
 * Add more buttons as needed for future tools.
 */
const Toolbar: React.FC<ToolbarProps> = ({ onImportClick }) => {
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
      <Tooltip title="Import GeoPackage">
        <IconButton color="primary" onClick={onImportClick} size="large">
          <CloudUploadIcon />
        </IconButton>
      </Tooltip>
      {/* Future: Add more tool buttons here */}
    </Box>
  );
};

export default Toolbar;
