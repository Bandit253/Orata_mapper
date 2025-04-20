import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ImportDialog from '../../components/mapview/ImportDialog';

describe('ImportDialog', () => {
  const baseProps = {
    open: true,
    fileToUpload: null,
    uploadStatus: 'idle' as const,
    uploadError: null,
    onFileChange: jest.fn(),
    onClose: jest.fn(),
    onUpload: jest.fn(),
  };

  it('renders file input and buttons', () => {
    render(<ImportDialog {...baseProps} />);
    expect(screen.getByText('Import GeoPackage File')).toBeInTheDocument();
    expect(screen.getByText('Select .gpkg File')).toBeInTheDocument();
    expect(screen.getByText('Import')).toBeInTheDocument();
  });

  it('calls onFileChange when file selected', () => {
    render(<ImportDialog {...baseProps} />);
    const input = screen.getByLabelText('Select .gpkg File', { selector: 'input[type="file"]' });
    fireEvent.change(input, { target: { files: [new File([''], 'test.gpkg')] } });
    expect(baseProps.onFileChange).toHaveBeenCalled();
  });

  it('calls onUpload when Import clicked', () => {
    render(<ImportDialog {...baseProps} fileToUpload={new File([''], 'test.gpkg')} />);
    fireEvent.click(screen.getByText('Import'));
    expect(baseProps.onUpload).toHaveBeenCalled();
  });

  it('shows error message if uploadError is set', () => {
    render(<ImportDialog {...baseProps} uploadError="Upload failed" uploadStatus="error" />);
    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });
});
