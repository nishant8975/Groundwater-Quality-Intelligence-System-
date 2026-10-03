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

export const fetchExceedances = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/exceedances', { params });
};

export const fetchExtremes = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/extremes', { params });
};

export const fetchDataQuality = (): Promise<ApiResponse<any>> => {
  return apiClient.get('/data-quality');
};

export const fetchParameters = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/parameters');
};
""",

    'frontend/src/hooks/useWawqi.ts': """import { useQuery } from '@tanstack/react-query';
import { fetchOverview, fetchCategories, fetchStates, fetchExceedances, fetchExtremes, fetchDataQuality, fetchParameters } from '../api/endpoints';

export const useOverview = () => {
  return useQuery({ queryKey: ['overview'], queryFn: fetchOverview });
};

export const useCategories = () => {
  return useQuery({ queryKey: ['categories'], queryFn: fetchCategories });
};

export const useStates = () => {
  return useQuery({ queryKey: ['states'], queryFn: fetchStates });
};

export const useExceedances = (filters: any = {}) => {
  return useQuery({ queryKey: ['exceedances', filters], queryFn: () => fetchExceedances(filters) });
};

export const useExtremes = (filters: any = {}) => {
  return useQuery({ queryKey: ['extremes', filters], queryFn: () => fetchExtremes(filters) });
};

export const useDataQuality = () => {
  return useQuery({ queryKey: ['dataQuality'], queryFn: fetchDataQuality });
};

export const useParameters = () => {
  return useQuery({ queryKey: ['parameters'], queryFn: fetchParameters });
};
""",

    'frontend/src/pages/Dashboard.tsx': """import { useOverview, useCategories, useStates } from '../hooks/useWawqi';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { Card } from '../components/ui/Card';
import { CategoryBadge } from '../components/ui/Badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const CATEGORY_COLORS: Record<string, string> = {
  'Excellent': '#34D399',
  'Good': '#60A5FA',
  'Poor': '#FBBF24',
  'Very Poor': '#F97316',
  'Unsuitable': '#EF4444',
  'UNAVAILABLE': '#64748B'
};

export default function Dashboard() {
  const { data: overviewResp, isLoading: isLoadingOverview, error: errorOverview } = useOverview();
  const { data: catResp, isLoading: isLoadingCat } = useCategories();
  const { data: statesResp, isLoading: isLoadingStates } = useStates();

  if (isLoadingOverview || isLoadingCat || isLoadingStates) return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-64" />
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );

  if (errorOverview) return <ErrorState message="Failed to load dashboard data." />;

  const stats = overviewResp?.data;
  const categories = catResp?.data || [];
  const states = statesResp?.data || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Groundwater Quality Intelligence</h1>
        <p className="mt-1 text-slate-400">Phase 8 Analytics Dashboard - National Overview</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Samples" value={stats?.total_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Available" value={stats?.eligible_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Unavailable" value={stats?.unavailable_samples?.toLocaleString() || 0} />
        <StatCard title="States / UTs" value={states.length} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-medium text-white mb-6">Category Distribution</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                <XAxis type="number" stroke="#94A3B8" />
                <YAxis dataKey="category" type="category" stroke="#94A3B8" width={100} />
                <Tooltip 
                  cursor={{fill: '#1E293B'}} 
                  contentStyle={{backgroundColor: '#0F172A', borderColor: '#334155', color: '#F8FAFC'}} 
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {categories.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.category] || CATEGORY_COLORS['UNAVAILABLE']} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        
        <Card>
          <h3 className="text-lg font-medium text-white mb-6">WQI Statistical Summary</h3>
          <p className="text-sm text-slate-400 mb-4">Note: The mean WQI is strongly influenced by extreme values in the unsuitably high tail.</p>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">Minimum</span>
              <span className="text-white font-medium">{stats?.min_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">Median</span>
              <span className="text-white font-medium">{stats?.median_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">Mean</span>
              <span className="text-white font-medium">{stats?.mean_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">75th Percentile</span>
              <span className="text-white font-medium">{stats?.p75_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">90th Percentile</span>
              <span className="text-white font-medium">{stats?.p90_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">95th Percentile</span>
              <span className="text-white font-medium">{stats?.p95_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">99th Percentile</span>
              <span className="text-white font-medium">{stats?.p99_wqi}</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-slate-300">Maximum</span>
              <span className="text-white font-medium text-red-400">{stats?.max_wqi}</span>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-medium text-white mb-2">WAWQI Distribution (Visualization)</h3>
        <p className="text-sm text-slate-400 mb-6">Display range 0–200. Values above 200 exist but are visually excluded from this histogram to maintain readability. The underlying data remains strictly unmodified.</p>
        <div className="h-64 flex items-center justify-center border border-dashed border-slate-700 rounded bg-slate-800/50">
           <span className="text-slate-500">Distribution Histogram Placeholder (Requires specialized binning from backend)</span>
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-medium text-white mb-4">State Overview</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-700">
            <thead>
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">State/UT</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Samples</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">WAWQI Available</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Median WAWQI</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Unsuitable Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {states.map((state: any) => {
                const unsuitablePct = state.eligible_samples > 0 
                  ? ((state.c_uns / state.eligible_samples) * 100).toFixed(1) 
                  : '0.0';
                return (
                  <tr key={state.state} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white">{state.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.total_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.eligible_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.median_wqi}</td>
                    <td className="px-3 py-4 text-sm text-red-400 text-right">{unsuitablePct}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
""",

    'frontend/src/pages/Extremes.tsx': """import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useExtremes } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';
import { CategoryBadge } from '../components/ui/Badge';

export default function Extremes() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get('page') || '1', 10);
  const minWqi = searchParams.get('min_wqi') || '100';

  const { data: resp, isLoading, error } = useExtremes({ page, limit: 50, min_wqi: minWqi });

  const handleNextPage = () => {
    setSearchParams(prev => { prev.set('page', (page + 1).toString()); return prev; });
  };
  const handlePrevPage = () => {
    setSearchParams(prev => { prev.set('page', Math.max(1, page - 1).toString()); return prev; });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Extreme WAWQI Observations</h1>
        <p className="mt-1 text-sm text-slate-400">Historical records exceeding Unsuitable thresholds. These are not automatically erroneous.</p>
      </div>

      <Card>
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Minimum WQI Filter:</span>
            <input 
              type="number" 
              value={minWqi} 
              onChange={(e) => setSearchParams({ min_wqi: e.target.value, page: '1' })}
              className="bg-slate-900 border border-slate-700 text-white rounded px-2 py-1 text-sm w-24"
            />
          </div>
          {resp?.pagination && (
            <div className="flex gap-2">
               <button onClick={handlePrevPage} disabled={page <= 1} className="px-3 py-1 bg-slate-800 text-white text-sm rounded disabled:opacity-50">Prev</button>
               <span className="px-3 py-1 text-slate-400 text-sm">Page {page} of {resp.pagination.totalPages}</span>
               <button onClick={handleNextPage} disabled={page >= resp.pagination.totalPages} className="px-3 py-1 bg-slate-800 text-white text-sm rounded disabled:opacity-50">Next</button>
            </div>
          )}
        </div>

        {isLoading ? <Skeleton className="h-96 w-full" /> : error ? <ErrorState message="Failed to load extreme values." /> : resp?.data?.length === 0 ? <EmptyState message="No extreme values found matching criteria." /> : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Station</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Location</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Date</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">WAWQI</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Category</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Dominant Factor</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Flags</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {resp?.data.map((row: any) => (
                  <tr key={row.sample_id} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm text-white max-w-[150px] truncate" title={row.station_name}>{row.station_name}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{row.district}, {row.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{new Date(row.sample_date).toLocaleDateString()}</td>
                    <td className="px-3 py-4 text-sm font-bold text-red-400 text-right">{row.wqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300"><CategoryBadge category={row.category} /></td>
                    <td className="px-3 py-4 text-sm text-slate-300">{row.dominant_parameter || 'N/A'}</td>
                    <td className="px-3 py-4 text-sm">
                       {row.data_quality_flags ? (
                         <span className="text-amber-500 font-medium" title={row.data_quality_flags}>Warning</span>
                       ) : <span className="text-slate-600">None</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
""",

    'frontend/src/pages/Exceedances.tsx': """import { useExceedances } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';

export default function Exceedances() {
  const { data: resp, isLoading, error } = useExceedances();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parameter Exceedances</h1>
        <p className="mt-1 text-sm text-slate-400">Valid observations breaching established BIS IS 10500 standards. Note: pH exceedances account for both lower and upper bounds.</p>
      </div>

      <Card>
        {isLoading ? <Skeleton className="h-64 w-full" /> : error ? <ErrorState message="Failed to load exceedances." /> : resp?.data?.length === 0 ? <EmptyState message="No data." /> : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Parameter</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Valid Observations</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Exceedances</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Exceedance %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {resp?.data.map((row: any) => (
                  <tr key={row.parameter} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white capitalize">{row.parameter}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{row.valid_observation_count?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{row.exceedance_count?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-amber-400 text-right font-medium">{row.exceedance_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
""",

    'frontend/src/pages/DataQuality.tsx': """import { useDataQuality } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { AlertCircle } from 'lucide-react';

export default function DataQuality() {
  const { data: resp, isLoading, error } = useDataQuality();

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message="Failed to load data quality metrics." />;
  
  const d = resp?.data || {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Data Quality Intelligence</h1>
        <p className="mt-1 text-sm text-slate-400">Scientific separation of data limitations from WAWQI outcomes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="WAWQI Unavailable" value={d.unavailable_samples?.toLocaleString() || 0} subtitle="< 6 Valid Parameters" />
        <StatCard title="Invalid Coordinates" value={d.invalid_coordinates?.toLocaleString() || 0} subtitle="Null Lat/Long" />
        <StatCard title="Total Observations" value="1.6M+" subtitle="Processed" />
      </div>

      <Card className="border-amber-900/50 bg-amber-950/10">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-amber-500 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-medium text-amber-500">Important Scientific Distinction</h3>
            <p className="mt-2 text-sm text-slate-300">
              Samples marked as <strong>UNAVAILABLE</strong> do not represent a WQI score of 0. They indicate insufficient parameter coverage (less than 6 core/conditional parameters). Imputing zeros for missing data artificially inflates water quality, a practice strictly prohibited in this methodology.
            </p>
          </div>
        </div>
      </Card>
      
      {d.flagged_sample_1419 && (
        <Card className="border-red-900/50 bg-red-950/10">
           <h3 className="text-lg font-medium text-red-500 mb-2">Dataset Anomaly Record</h3>
           <p className="text-sm text-slate-300 mb-2">Sample 1419 is retained in its original form per source extraction methodology, but flags are attached:</p>
           <code className="text-xs bg-slate-900 p-2 rounded text-slate-400 block break-words">
             {d.flagged_sample_1419}
           </code>
        </Card>
      )}
    </div>
  );
}
"""
}

# Write files with UTF-8 encoding
for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Dashboard UI files generated successfully.")
