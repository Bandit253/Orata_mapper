import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MapView from '../components/MapView';

// Mock maplibre-gl to avoid rendering actual maps in tests
jest.mock('maplibre-gl', () => {
  return {
    Map: jest.fn().mockImplementation(() => ({
      on: jest.fn(),
      remove: jest.fn(),
      addControl: jest.fn(),
      setStyle: jest.fn(),
      getStyle: jest.fn(() => ({ layers: [] })),
      getZoom: jest.fn(() => 10),
      getCenter: jest.fn(() => ({ lng: 144.9631, lat: -37.8136 })),
      project: jest.fn(() => ({ x: 0, y: 0 })),
      unproject: jest.fn(() => ({ lng: 144.9631, lat: -37.8136 })),
      getBounds: jest.fn(() => ({
        getNorthEast: jest.fn(() => ({ lng: 145, lat: -37 })),
        getSouthWest: jest.fn(() => ({ lng: 144, lat: -38 }))
      })),
      resize: jest.fn(),
    })),
    NavigationControl: jest.fn(),
    StyleSpecification: {},
  };
});

describe('MapView', () => {
  it('renders without crashing', () => {
    render(<MapView />);
    expect(screen.getByText(/OpenStreetMap/i)).toBeInTheDocument();
  });

  it('shows basemap options', () => {
    render(<MapView />);
    expect(screen.getByText('OpenStreetMap')).toBeInTheDocument();
    expect(screen.getByText('Google Satellite')).toBeInTheDocument();
  });

  it('opens and closes the buffer dialog', async () => {
    render(<MapView />);
    // Open buffer dialog
    const bufferButton = screen.getByRole('button', { name: /buffer/i });
    fireEvent.click(bufferButton);
    expect(await screen.findByText(/Buffer Distance/i)).toBeInTheDocument();
    // Close dialog
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    await waitFor(() => {
      expect(screen.queryByText(/Buffer Distance/i)).not.toBeInTheDocument();
    });
  });

  // Add more tests as needed for layer visibility, error handling, etc.
});
