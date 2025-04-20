import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LayerList, { LayerEntry } from '../../components/mapview/LayerList';

describe('LayerList', () => {
  const layers: LayerEntry[] = [
    { tableName: 'roads', visible: true, loading: false },
    { tableName: 'buildings', visible: false, loading: false },
  ];
  const contextMenu = {
    mouseX: 100,
    mouseY: 200,
    tableName: 'roads',
  };
  const onContextMenu = jest.fn();
  const onToggleVisibility = jest.fn();
  const onRemoveLayer = jest.fn();
  const onCloseContextMenu = jest.fn();

  it('renders all layers', () => {
    render(
      <LayerList
        layers={layers}
        contextMenu={null}
        onContextMenu={onContextMenu}
        onToggleVisibility={onToggleVisibility}
        onRemoveLayer={onRemoveLayer}
        onCloseContextMenu={onCloseContextMenu}
      />
    );
    expect(screen.getByText('roads')).toBeInTheDocument();
    expect(screen.getByText('buildings')).toBeInTheDocument();
  });

  it('calls onToggleVisibility when eye icon clicked', () => {
    render(
      <LayerList
        layers={layers}
        contextMenu={null}
        onContextMenu={onContextMenu}
        onToggleVisibility={onToggleVisibility}
        onRemoveLayer={onRemoveLayer}
        onCloseContextMenu={onCloseContextMenu}
      />
    );
    const buttons = screen.getAllByTitle(/Show Layer|Hide Layer/);
    fireEvent.click(buttons[0]);
    expect(onToggleVisibility).toHaveBeenCalledWith('roads');
  });

  it('calls onRemoveLayer from context menu', () => {
    render(
      <LayerList
        layers={layers}
        contextMenu={contextMenu}
        onContextMenu={onContextMenu}
        onToggleVisibility={onToggleVisibility}
        onRemoveLayer={onRemoveLayer}
        onCloseContextMenu={onCloseContextMenu}
      />
    );
    fireEvent.click(screen.getByText('Remove from Map'));
    expect(onRemoveLayer).toHaveBeenCalledWith('roads');
  });
});
