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
""",

    'frontend/src/hooks/useWawqi.ts': """import { useQuery } from '@tanstack/react-query';
import { 
  fetchOverview, fetchCategories, fetchStates, fetchStateDetail, 
  fetchDistricts, fetchDistrictDetail, fetchParameters, 
  fetchParameterDetail, fetchExceedances, fetchExtremes, 
  fetchDataQuality, fetchTemporal 
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
""",

    'frontend/src/components/ui/FilterBar.tsx': """import { useSearchParams } from 'react-router-dom';

interface FilterConfig {
  showState?: boolean;
  showDistrict?: boolean;
  showCategory?: boolean;
  showParameter?: boolean;
  statesList?: string[];
  parametersList?: string[];
}

export const FilterBar = ({ config }: { config: FilterConfig }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const handleFilterChange = (key: string, value: string) => {
    setSearchParams(prev => {
      if (value) prev.set(key, value);
      else prev.delete(key);
      if (key === 'state') prev.delete('district'); // reset district on state change
      prev.set('page', '1'); // reset pagination
      return prev;
    });
  };

  const handleReset = () => {
    setSearchParams({});
  };

  return (
    <div className="flex flex-wrap items-center gap-4 bg-slate-800 p-4 rounded border border-slate-700">
      <span className="text-sm font-medium text-slate-300">Filters:</span>
      
      {config.showState && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('state') || ''}
          onChange={e => handleFilterChange('state', e.target.value)}
        >
          <option value="">All States</option>
          {config.statesList?.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      )}

      {config.showDistrict && searchParams.get('state') && (
        <input 
          type="text"
          placeholder="District name..."
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm"
          value={searchParams.get('district') || ''}
          onChange={e => handleFilterChange('district', e.target.value)}
        />
      )}

      {config.showCategory && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('category') || ''}
          onChange={e => handleFilterChange('category', e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="Excellent">Excellent</option>
          <option value="Good">Good</option>
          <option value="Poor">Poor</option>
          <option value="Very Poor">Very Poor</option>
          <option value="Unsuitable">Unsuitable</option>
        </select>
      )}

      {config.showParameter && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('parameter') || ''}
          onChange={e => handleFilterChange('parameter', e.target.value)}
        >
          <option value="">All Parameters</option>
          {config.parametersList?.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
        </select>
      )}

      {Array.from(searchParams.keys()).length > 0 && (
        <button 
          onClick={handleReset}
          className="text-sm text-slate-400 hover:text-white underline ml-auto"
        >
          Reset Filters
        </button>
      )}
    </div>
  );
};
""",

    'frontend/src/pages/Dashboard.tsx': """import { useOverview, useCategories, useStates } from '../hooks/useWawqi';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { Card } from '../components/ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';

const CATEGORY_COLORS: Record<string, string> = {
  'Excellent': '#34D399',
  'Good': '#60A5FA',
  'Poor': '#FBBF24',
  'Very Poor': '#F97316',
  'Unsuitable': '#EF4444',
  'UNAVAILABLE': '#64748B'
};

const WQI_BINS: Record<string, string> = {
  'Excellent': '0–50',
  'Good': '50–100',
  'Poor': '100–200',
  'Very Poor': '200–300',
  'Unsuitable': '> 300'
};

export default function Dashboard() {
  const { data: overviewResp, isLoading: isLoadingOverview, error: errorOverview } = useOverview();
  const { data: catResp, isLoading: isLoadingCat } = useCategories();
  const { data: statesResp, isLoading: isLoadingStates } = useStates();

  if (isLoadingOverview || isLoadingCat || isLoadingStates) return <Skeleton className="h-96 w-full" />;
  if (errorOverview) return <ErrorState message="Failed to load dashboard data." />;

  const stats = overviewResp?.data;
  const categories = catResp?.data || [];
  const states = statesResp?.data || [];

  // Transform categories to serve as distribution histogram
  const distributionData = categories.filter((c: any) => c.category !== 'UNAVAILABLE').map((c: any) => ({
    bin: WQI_BINS[c.category] || c.category,
    count: c.count,
    category: c.category
  }));

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
          <h3 className="text-lg font-medium text-white mb-2">WAWQI Binned Distribution</h3>
          <p className="text-sm text-slate-400 mb-6">Display range 0–300. Values above 300 exist (>300 bin). This visualization prevents unsuitably high extreme tails from breaking scale readability.</p>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="bin" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" />
                <Tooltip cursor={{fill: '#1E293B'}} contentStyle={{backgroundColor: '#0F172A', borderColor: '#334155', color: '#F8FAFC'}} />
                <Bar dataKey="count" name="Samples" radius={[4, 4, 0, 0]}>
                  {distributionData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.category]} />
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
        <h3 className="text-lg font-medium text-white mb-2">State Category Composition</h3>
        <p className="text-sm text-slate-400 mb-6">Showing top 10 states by total sample volume.</p>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={states.slice(0, 10)} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
              <XAxis type="number" stroke="#94A3B8" />
              <YAxis dataKey="state" type="category" stroke="#94A3B8" width={120} tick={{fontSize: 12}} />
              <Tooltip cursor={{fill: '#1E293B'}} contentStyle={{backgroundColor: '#0F172A', borderColor: '#334155', color: '#F8FAFC'}} />
              <Legend />
              <Bar dataKey="c_exc" name="Excellent" stackId="a" fill={CATEGORY_COLORS['Excellent']} />
              <Bar dataKey="c_good" name="Good" stackId="a" fill={CATEGORY_COLORS['Good']} />
              <Bar dataKey="c_poor" name="Poor" stackId="a" fill={CATEGORY_COLORS['Poor']} />
              <Bar dataKey="c_vpoor" name="Very Poor" stackId="a" fill={CATEGORY_COLORS['Very Poor']} />
              <Bar dataKey="c_uns" name="Unsuitable" stackId="a" fill={CATEGORY_COLORS['Unsuitable']} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-white">State Analytics Summary</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-700">
            <thead>
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">State/UT</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Samples</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Available</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Unavailable</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Median</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Mean</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Excellent %</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Good %</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Poor %</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Very Poor %</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Unsuitable %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {states.map((s: any) => {
                const total = s.eligible_samples || 1; // avoid / 0
                return (
                  <tr key={s.state} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white">{s.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{s.total_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{s.eligible_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{s.unavailable_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{s.median_wqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{s.mean_wqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{((s.c_exc / total) * 100).toFixed(1)}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{((s.c_good / total) * 100).toFixed(1)}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{((s.c_poor / total) * 100).toFixed(1)}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{((s.c_vpoor / total) * 100).toFixed(1)}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{((s.c_uns / total) * 100).toFixed(1)}%</td>
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

    'frontend/src/pages/Districts.tsx': """import { useSearchParams } from 'react-router-dom';
import { useStates, useDistricts } from '../hooks/useWawqi';
import { FilterBar } from '../components/ui/FilterBar';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';

export default function Districts() {
  const [searchParams] = useSearchParams();
  const state = searchParams.get('state') || undefined;
  
  const { data: statesResp } = useStates();
  const statesList = statesResp?.data?.map((s: any) => s.state) || [];
  
  const { data: resp, isLoading, error } = useDistricts({ state });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">District Analytics</h1>
        <p className="mt-1 text-sm text-slate-400">Aggregated WAWQI statistics at the district level.</p>
      </div>

      <FilterBar config={{ showState: true, statesList }} />

      <Card>
        {isLoading ? <Skeleton className="h-96 w-full" /> : error ? <ErrorState message="Failed to load districts." /> : resp?.data?.length === 0 ? <EmptyState message="No districts found." /> : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">District</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">State</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Samples</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Available</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Unavailable</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Median</th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Mean</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {resp?.data.map((d: any, idx: number) => (
                  <tr key={`${d.district}-${d.state}-${idx}`} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white">{d.district}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{d.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.total_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.eligible_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.unavailable_samples?.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.median_wqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.mean_wqi}</td>
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

    'frontend/src/pages/Parameters.tsx': """import { useParameters } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';

export default function Parameters() {
  const { data: resp, isLoading, error } = useParameters();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parameter Analytics</h1>
        <p className="mt-1 text-sm text-slate-400">Canonical WAWQI parameter limits and standard references. Detailed parameter distribution requires drill-down.</p>
      </div>

      <Card>
        {isLoading ? <Skeleton className="h-96 w-full" /> : error ? <ErrorState message="Failed to load parameters." /> : resp?.data?.length === 0 ? <EmptyState message="No parameters found." /> : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Parameter</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Name</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Unit</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Regulatory Standard</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">Limit Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {resp?.data.map((p: any) => (
                  <tr key={p.canonical_name} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white">{p.canonical_name}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{p.display_name}</td>
                    <td className="px-3 py-4 text-sm text-slate-300">{p.unit}</td>
                    <td className="px-3 py-4 text-sm font-medium text-amber-400">{p.standard}</td>
                    <td className="px-3 py-4 text-sm text-slate-400">{p.limit_type}</td>
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

    'frontend/src/pages/Exceedances.tsx': """import { useSearchParams } from 'react-router-dom';
import { useExceedances, useStates } from '../hooks/useWawqi';
import { FilterBar } from '../components/ui/FilterBar';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';

export default function Exceedances() {
  const [searchParams] = useSearchParams();
  const state = searchParams.get('state') || undefined;
  const district = searchParams.get('district') || undefined;
  const parameter = searchParams.get('parameter') || undefined;
  
  const { data: statesResp } = useStates();
  const statesList = statesResp?.data?.map((s: any) => s.state) || [];
  
  const { data: resp, isLoading, error } = useExceedances({ state, district, parameter });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Parameter Exceedances</h1>
        <p className="mt-1 text-sm text-slate-400">Valid observations breaching established BIS IS 10500 standards. Note: pH exceedances account for both lower and upper bounds natively.</p>
      </div>

      <FilterBar config={{ showState: true, showDistrict: true, showParameter: true, statesList, parametersList: ['ph', 'chloride', 'sulphate', 'hardness', 'calcium', 'magnesium', 'iron', 'arsenic', 'uranium'] }} />

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

    'frontend/src/App.tsx': """import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import StatesOverview from './pages/StatesOverview';
import Districts from './pages/Districts';
import Parameters from './pages/Parameters';
import Exceedances from './pages/Exceedances';
import Extremes from './pages/Extremes';
import DataQuality from './pages/DataQuality';
import MapPage from './pages/MapPage';

export default function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/states" element={<StatesOverview />} />
          <Route path="/districts" element={<Districts />} />
          <Route path="/parameters" element={<Parameters />} />
          <Route path="/exceedances" element={<Exceedances />} />
          <Route path="/extremes" element={<Extremes />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="*" element={
            <div className="flex items-center justify-center h-96">
              <h2 className="text-2xl text-slate-400">404 - Page Not Found</h2>
            </div>
          } />
        </Routes>
      </AppLayout>
    </Router>
  );
}
"""
}

# Write files with UTF-8 encoding
for filepath, content in files.items():
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Dashboard UI files V2 generated successfully.")
