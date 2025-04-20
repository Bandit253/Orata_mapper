import maplibregl from 'maplibre-gl';
import axios from 'axios';
import { LayerEntry } from './LayerList';

/**
 * Expand a bounding box by a percentage.
 */
export function expand(min: number, max: number, pct: number): [number, number] {
  const center = (min + max) / 2;
  const half = (max - min) / 2 * (1 + pct);
  return [center - half, center + half];
}

/**
 * Fetch features for a table within the current bbox (+5%) and add to map.
 */
export async function fetchAndShowLayer(map: maplibregl.Map, tableName: string, setLayers: (fn: (layers: LayerEntry[]) => LayerEntry[]) => void) {
  const bounds = map.getBounds();
  const [minLng, maxLng] = expand(bounds.getWest(), bounds.getEast(), 0.05);
  const [minLat, maxLat] = expand(bounds.getSouth(), bounds.getNorth(), 0.05);
  try {
    const resp = await axios.post(`/features/${tableName}/query/bbox`, {
      bbox: [minLng, minLat, maxLng, maxLat],
    });
    const geojson = resp.data;
    // Remove existing source/layer if present
    if (map.getSource(tableName)) {
      map.removeLayer(tableName);
      map.removeSource(tableName);
    }
    map.addSource(tableName, {
      type: 'geojson',
      data: geojson,
    });
    map.addLayer({
      id: tableName,
      type: 'circle',
      source: tableName,
      paint: {
        'circle-radius': 6,
        'circle-color': '#1976d2',
        'circle-stroke-width': 2,
        'circle-stroke-color': '#fff',
      },
    });
  } catch (err) {
    console.error('Failed to fetch features for', tableName, err);
    setLayers(currentLayers => currentLayers.map(l => l.tableName === tableName ? { ...l, error: 'Failed to fetch features' } : l));
  }
}
