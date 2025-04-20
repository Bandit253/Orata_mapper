import React from 'react';
import { Paper, Box, Typography, List, ListItem, ListItemText, IconButton, Menu, MenuItem } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

export interface LayerEntry {
  tableName: string;
  visible: boolean;
  loading: boolean;
  error?: string;
}

interface LayerListProps {
  layers: LayerEntry[];
  contextMenu: {
    mouseX: number;
    mouseY: number;
    tableName: string | null;
  } | null;
  onContextMenu: (event: React.MouseEvent, tableName: string) => void;
  onToggleVisibility: (tableName: string) => void;
  onRemoveLayer: (tableName: string) => void;
  onCloseContextMenu: () => void;
}

/**
 * Sidebar Table of Contents and context menu for layers.
 */
const LayerList: React.FC<LayerListProps> = ({
  layers,
  contextMenu,
  onContextMenu,
  onToggleVisibility,
  onRemoveLayer,
  onCloseContextMenu
}) => (
  <Paper
    elevation={1}
    sx={{ flex: 1, overflowY: 'auto', p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}
  >
    <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center', mb: 1, gap: 1 }}>
      <Typography variant="h6" sx={{ fontWeight: 600 }}>
        Table of Contents
      </Typography>
    </Box>
    <List>
      {layers.map((layer: LayerEntry) => (
        <ListItem
          key={layer.tableName}
          onContextMenu={e => onContextMenu(e, layer.tableName)}
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
              onToggleVisibility(layer.tableName);
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
      onClose={onCloseContextMenu}
      anchorReference="anchorPosition"
      anchorPosition={
        contextMenu !== null
          ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
          : undefined
      }
      MenuListProps={{ 'aria-labelledby': 'layer-context-menu' }}
    >
      <MenuItem
        onClick={() => contextMenu && onToggleVisibility(contextMenu.tableName!)}
        disabled={!contextMenu}
      >
        {contextMenu && layers.find(l => l.tableName === contextMenu.tableName)?.visible
          ? 'Hide Layer'
          : 'Show Layer'}
      </MenuItem>
      <MenuItem
        onClick={() => contextMenu && onRemoveLayer(contextMenu.tableName!)}
        disabled={!contextMenu}
      >
        Remove from Map
      </MenuItem>
    </Menu>
  </Paper>
);

export default LayerList;
