import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import BufferDialog from '../../components/mapview/BufferDialog';

describe('BufferDialog', () => {
  const baseProps = {
    open: true,
    geometry: '',
    distance: 100,
    loading: false,
    error: null,
    onGeometryChange: jest.fn(),
    onDistanceChange: jest.fn(),
    onClose: jest.fn(),
    onSubmit: jest.fn(),
  };

  it('renders dialog with fields', () => {
    render(<BufferDialog {...baseProps} />);
    expect(screen.getByText('Buffer Tool')).toBeInTheDocument();
    expect(screen.getByLabelText('Geometry (GeoJSON)')).toBeInTheDocument();
    expect(screen.getByLabelText('Buffer Distance (meters)')).toBeInTheDocument();
    expect(screen.getByText('Run Buffer')).toBeInTheDocument();
  });

  it('calls onGeometryChange when geometry changes', () => {
    render(<BufferDialog {...baseProps} />);
    fireEvent.change(screen.getByLabelText('Geometry (GeoJSON)'), { target: { value: '{"type": "Point"}' } });
    expect(baseProps.onGeometryChange).toHaveBeenCalledWith('{"type": "Point"}');
  });

  it('calls onDistanceChange when distance changes', () => {
    render(<BufferDialog {...baseProps} />);
    fireEvent.change(screen.getByLabelText('Buffer Distance (meters)'), { target: { value: '250' } });
    expect(baseProps.onDistanceChange).toHaveBeenCalledWith(250);
  });

  it('calls onSubmit when Run Buffer clicked', () => {
    render(<BufferDialog {...baseProps} />);
    fireEvent.click(screen.getByText('Run Buffer'));
    expect(baseProps.onSubmit).toHaveBeenCalled();
  });

  it('shows error message if error prop is set', () => {
    render(<BufferDialog {...baseProps} error="Invalid GeoJSON" />);
    expect(screen.getByText('Invalid GeoJSON')).toBeInTheDocument();
  });
});
