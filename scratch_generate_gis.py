import os

files = {
    'frontend/src/api/endpoints.ts': """import { apiClient } from './client';
import type { ApiResponse, OverviewStats } from '../types';

export const fetchOverview = (): Promise<ApiResponse<OverviewStats>> => {
  return apiClient.get('/overview');
};

export const fetchCategories = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/wawqi/categories');
};

export const fetchStates = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/states');
};

export const fetchStateDetail = (state: string): Promise<ApiResponse<any>> => {
  return apiClient.get(`/states/${encodeURIComponent(state)}`);
};

export const fetchDistricts = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/districts', { params });
};

export const fetchDistrictDetail = (district: string, state?: string): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/districts/${encodeURIComponent(district)}`, { params: { state } });
};

export const fetchParameters = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/parameters');
};

export const fetchParameterDetail = (parameter: string, params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/parameters/${encodeURIComponent(parameter)}`, { params });
};

export const fetchExceedances = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/exceedances', { params });
};

export const fetchExtremes = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/extremes', { params });
};

export const fetchDataQuality = (): Promise<ApiResponse<any>> => {
  return apiClient.get('/data-quality');
};

export const fetchTemporal = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/temporal');
};

export const fetchGis = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/gis', { params });
};
""",

    'frontend/src/hooks/useWawqi.ts': """import { useQuery } from '@tanstack/react-query';
import { 
  fetchOverview, fetchCategories, fetchStates, fetchStateDetail, 
  fetchDistricts, fetchDistrictDetail, fetchParameters, 
  fetchParameterDetail, fetchExceedances, fetchExtremes, 
  fetchDataQuality, fetchTemporal, fetchGis 
} from '../api/endpoints';

export const useOverview = () => useQuery({ queryKey: ['overview'], queryFn: fetchOverview });
export const useCategories = () => useQuery({ queryKey: ['categories'], queryFn: fetchCategories });
export const useStates = () => useQuery({ queryKey: ['states'], queryFn: fetchStates });
export const useStateDetail = (state: string) => useQuery({ queryKey: ['state', state], queryFn: () => fetchStateDetail(state), enabled: !!state });
export const useDistricts = (filters: any = {}) => useQuery({ queryKey: ['districts', filters], queryFn: () => fetchDistricts(filters) });
export const useDistrictDetail = (district: string, state?: string) => useQuery({ queryKey: ['district', district, state], queryFn: () => fetchDistrictDetail(district, state), enabled: !!district });
export const useParameters = () => useQuery({ queryKey: ['parameters'], queryFn: fetchParameters });
export const useParameterDetail = (parameter: string, filters: any = {}) => useQuery({ queryKey: ['parameter', parameter, filters], queryFn: () => fetchParameterDetail(parameter, filters), enabled: !!parameter });
export const useExceedances = (filters: any = {}) => useQuery({ queryKey: ['exceedances', filters], queryFn: () => fetchExceedances(filters) });
export const useExtremes = (filters: any = {}) => useQuery({ queryKey: ['extremes', filters], queryFn: () => fetchExtremes(filters) });
export const useDataQuality = () => useQuery({ queryKey: ['dataQuality'], queryFn: fetchDataQuality });
export const useTemporal = () => useQuery({ queryKey: ['temporal'], queryFn: fetchTemporal });
export const useGis = (filters: any = {}) => useQuery({ queryKey: ['gis', filters], queryFn: () => fetchGis(filters) });
""",

    'frontend/src/pages/MapPage.tsx': """import React, { useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useGis, useStates } from '../hooks/useWawqi';
import { FilterBar } from '../components/ui/FilterBar';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';
import { CategoryBadge } from '../components/ui/Badge';

const CATEGORY_COLORS: Record<string, string> = {
  'Excellent': '#34D399',
  'Good': '#60A5FA',
  'Poor': '#FBBF24',
  'Very Poor': '#F97316',
  'Unsuitable': '#EF4444',
  'UNAVAILABLE': '#64748B'
};

function MapBoundsFitter({ points, fitToDataTrig }: { points: any[], fitToDataTrig: number }) {
  const map = useMap();
  useEffect(() => {
    if (points && points.length > 0) {
      const bounds = L.latLngBounds(points.map(p => [p.latitude, p.longitude]));
      map.fitBounds(bounds, { padding: [20, 20], maxZoom: 12 });
    }
  }, [points, fitToDataTrig, map]);
  return null;
}

export default function MapPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const state = searchParams.get('state') || undefined;
  const district = searchParams.get('district') || undefined;
  const category = searchParams.get('category') || undefined;
  const page = parseInt(searchParams.get('page') || '1', 10);
  
  const [fitTrigger, setFitTrigger] = React.useState(0);

  const { data: statesResp } = useStates();
  const statesList = statesResp?.data?.map((s: any) => s.state) || [];
  
  const { data: resp, isLoading, error } = useGis({ state, district, category, page, limit: 100 });
  const points = resp?.data || [];
  const pagination = resp?.pagination;

  const validPoints = useMemo(() => {
    return points.filter((p: any) => p.latitude != null && p.longitude != null && !isNaN(p.latitude) && !isNaN(p.longitude));
  }, [points]);

  const handleNextPage = () => setSearchParams(prev => { prev.set('page', (page + 1).toString()); return prev; });
  const handlePrevPage = () => setSearchParams(prev => { prev.set('page', Math.max(1, page - 1).toString()); return prev; });

  const stats = useMemo(() => {
    return validPoints.reduce((acc: any, curr: any) => {
      acc[curr.category] = (acc[curr.category] || 0) + 1;
      return acc;
    }, {});
  }, [validPoints]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">GIS Intelligence</h1>
        <p className="mt-1 text-sm text-slate-400">Geospatial analysis of groundwater quality. Data is paginated (100 points/page) to preserve performance.</p>
      </div>

      <FilterBar config={{ showState: true, showDistrict: true, showCategory: true, statesList }} />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 h-[600px] bg-slate-800 rounded border border-slate-700 relative overflow-hidden">
          {isLoading && <div className="absolute inset-0 z-10 bg-slate-900/50 flex items-center justify-center"><Skeleton className="h-full w-full" /></div>}
          {error && <div className="absolute inset-0 z-10 bg-slate-900 flex items-center justify-center"><ErrorState message="Failed to load GIS data" /></div>}
          
          <MapContainer center={[22.0, 79.0]} zoom={5} style={{ height: '100%', width: '100%', zIndex: 1 }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            />
            {validPoints.map((p: any) => (
              <CircleMarker
                key={p.location_id}
                center={[p.latitude, p.longitude]}
                radius={6}
                pathOptions={{
                  fillColor: CATEGORY_COLORS[p.category] || CATEGORY_COLORS['UNAVAILABLE'],
                  color: '#0F172A',
                  weight: 1,
                  fillOpacity: 0.8
                }}
              >
                <Popup className="text-sm">
                  <div className="font-semibold">{p.station_name}</div>
                  <div className="text-gray-600 mb-2">{p.district}, {p.state}</div>
                  <div className="font-bold text-gray-800">WQI: {p.wqi !== null ? p.wqi : 'Unavailable'}</div>
                  <div className="mb-2"><CategoryBadge category={p.category} /></div>
                  <div className="text-xs text-gray-500 border-t pt-1">Lat: {p.latitude.toFixed(4)}, Lng: {p.longitude.toFixed(4)}</div>
                  {p.wqi === null && <div className="text-xs text-amber-600 mt-1">⚠ Insufficient parameters</div>}
                </Popup>
              </CircleMarker>
            ))}
            <MapBoundsFitter points={validPoints} fitToDataTrig={fitTrigger} />
          </MapContainer>
        </div>

        <div className="space-y-4">
          <Card>
            <h3 className="text-lg font-medium text-white mb-4">Map Controls</h3>
            <button 
              onClick={() => setFitTrigger(prev => prev + 1)}
              disabled={validPoints.length === 0}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white py-2 rounded text-sm disabled:opacity-50"
            >
              Fit to Data
            </button>
          </Card>
          
          <Card>
            <h3 className="text-lg font-medium text-white mb-4">Visible Statistics</h3>
            <p className="text-xs text-slate-400 mb-4">Based on current API page ({validPoints.length} points)</p>
            <div className="space-y-2 text-sm">
               {['Excellent', 'Good', 'Poor', 'Very Poor', 'Unsuitable', 'UNAVAILABLE'].map(cat => (
                 <div key={cat} className="flex justify-between items-center">
                   <div className="flex items-center gap-2">
                     <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[cat] }}></div>
                     <span className="text-slate-300">{cat}</span>
                   </div>
                   <span className="text-white font-medium">{stats[cat] || 0}</span>
                 </div>
               ))}
            </div>
          </Card>
        </div>
      </div>

      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-white">GIS List View</h3>
          {pagination && (
            <div className="flex gap-2">
               <button onClick={handlePrevPage} disabled={page <= 1} className="px-3 py-1 bg-slate-800 text-white text-sm rounded disabled:opacity-50">Prev</button>
               <span className="px-3 py-1 text-slate-400 text-sm">Page {page} of {pagination.totalPages}</span>
               <button onClick={handleNextPage} disabled={page >= pagination.totalPages} className="px-3 py-1 bg-slate-800 text-white text-sm rounded disabled:opacity-50">Next</button>
            </div>
          )}
        </div>
        <div className="overflow-x-auto">
          {validPoints.length === 0 ? <EmptyState message="No valid locations found." /> : (
            <table className="min-w-full divide-y divide-slate-700">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Station</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Location</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">WAWQI</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Category</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Coordinates</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {validPoints.map((p: any) => (
                  <tr key={p.location_id} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white max-w-[200px] truncate" title={p.station_name}>{p.station_name}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{p.district}, {p.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{p.wqi !== null ? p.wqi : 'Unavailable'}</td>
                    <td className="px-3 py-4 text-sm text-slate-300"><CategoryBadge category={p.category} /></td>
                    <td className="px-3 py-4 text-sm text-slate-400 text-right">{p.latitude.toFixed(4)}, {p.longitude.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </Card>
    </div>
  );
}
"""
}

for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("GIS mapping files generated successfully.")
