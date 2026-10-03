import os

files = {
    'frontend/tailwind.config.js': """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A', // slate-900
        surface: '#1E293B',    // slate-800
        primary: '#38BDF8',    // sky-400
        wawqi: {
          excellent: '#34D399', // emerald-400
          good: '#60A5FA',      // blue-400
          poor: '#FBBF24',      // amber-400
          very_poor: '#F97316', // orange-500
          unsuitable: '#EF4444',// red-500
          unavailable: '#64748B'// slate-500
        }
      }
    },
  },
  plugins: [],
}
""",
    
    'frontend/postcss.config.js': """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""",

    'frontend/.env.example': """VITE_API_BASE_URL=http://localhost:3000/api
""",
    'frontend/.env': """VITE_API_BASE_URL=http://localhost:3000/api
""",

    'frontend/src/index.css': """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-background text-slate-200 antialiased;
  }
}

/* Leaflet override for dark mode */
.leaflet-container {
  background: #0F172A !important;
}
""",

    'frontend/src/main.tsx': """import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import 'leaflet/dist/leaflet.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
      retry: 1
    },
  },
})

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
""",

    'frontend/src/App.tsx': """import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import StatesOverview from './pages/StatesOverview'
import StateDetail from './pages/StateDetail'
import DistrictDetail from './pages/DistrictDetail'
import Parameters from './pages/Parameters'
import Exceedances from './pages/Exceedances'
import MapPage from './pages/MapPage'
import Extremes from './pages/Extremes'
import DataQuality from './pages/DataQuality'
import NotFound from './pages/NotFound'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="states" element={<StatesOverview />} />
          <Route path="states/:state" element={<StateDetail />} />
          <Route path="districts/:district" element={<DistrictDetail />} />
          <Route path="parameters" element={<Parameters />} />
          <Route path="exceedances" element={<Exceedances />} />
          <Route path="map" element={<MapPage />} />
          <Route path="extremes" element={<Extremes />} />
          <Route path="data-quality" element={<DataQuality />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
""",

    'frontend/src/types/index.ts': """
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface ApiResponse<T> {
  data: T;
  pagination?: PaginationMeta;
}

export type WawqiCategory = 'Excellent' | 'Good' | 'Poor' | 'Very Poor' | 'Unsuitable' | 'UNAVAILABLE';

export interface OverviewStats {
  total_samples: number;
  eligible_samples: number;
  unavailable_samples: number;
  state_count: number;
  district_count: number;
  location_count: number;
  min_wqi: number;
  max_wqi: number;
  mean_wqi: number;
  median_wqi: number;
  p25_wqi: number;
  p75_wqi: number;
  p90_wqi: number;
  p95_wqi: number;
  p99_wqi: number;
}
""",

    'frontend/src/api/client.ts': """import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    return Promise.reject(error.response?.data?.error || error.message);
  }
);
""",

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
""",

    'frontend/src/hooks/useWawqi.ts': """import { useQuery } from '@tanstack/react-query';
import { fetchOverview, fetchCategories, fetchStates } from '../api/endpoints';

export const useOverview = () => {
  return useQuery({
    queryKey: ['overview'],
    queryFn: fetchOverview,
  });
};

export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  });
};

export const useStates = () => {
  return useQuery({
    queryKey: ['states'],
    queryFn: fetchStates,
  });
};
""",

    'frontend/src/components/ui/Card.tsx': """import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn("bg-surface border border-slate-700 rounded-lg p-6 shadow-sm", className)}>
      {children}
    </div>
  );
}
""",

    'frontend/src/components/ui/StatCard.tsx': """import { Card } from './Card';
import React from 'react';

export function StatCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <Card>
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">{title}</h3>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-semibold text-white">{value}</span>
        {subtitle && <span className="text-sm text-slate-400">{subtitle}</span>}
      </div>
    </Card>
  );
}
""",

    'frontend/src/components/ui/Badge.tsx': """import { clsx } from 'clsx';
import { WawqiCategory } from '../../types';

export function CategoryBadge({ category }: { category: WawqiCategory | string }) {
  const styles = {
    'Excellent': 'bg-wawqi-excellent/10 text-wawqi-excellent border-wawqi-excellent/20',
    'Good': 'bg-wawqi-good/10 text-wawqi-good border-wawqi-good/20',
    'Poor': 'bg-wawqi-poor/10 text-wawqi-poor border-wawqi-poor/20',
    'Very Poor': 'bg-wawqi-very_poor/10 text-wawqi-very_poor border-wawqi-very_poor/20',
    'Unsuitable': 'bg-wawqi-unsuitable/10 text-wawqi-unsuitable border-wawqi-unsuitable/20',
    'UNAVAILABLE': 'bg-wawqi-unavailable/10 text-wawqi-unavailable border-wawqi-unavailable/20',
  };
  
  const defaultStyle = 'bg-slate-800 text-slate-300 border-slate-700';
  const appliedStyle = styles[category as keyof typeof styles] || defaultStyle;

  return (
    <span className={clsx("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border", appliedStyle)}>
      {category}
    </span>
  );
}
""",

    'frontend/src/components/ui/States.tsx': """import React from 'react';
import { AlertCircle, Database } from 'lucide-react';

export function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-700 rounded ${className}`} />;
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-red-950/20 rounded-lg border border-red-900/50">
      <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-red-400">Error Loading Data</h3>
      <p className="mt-1 text-sm text-red-300/80">{message}</p>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-surface/50 rounded-lg border border-slate-700 border-dashed">
      <Database className="w-12 h-12 text-slate-500 mb-4 opacity-50" />
      <h3 className="text-lg font-medium text-slate-300">No Data Available</h3>
      <p className="mt-1 text-sm text-slate-500">{message}</p>
    </div>
  );
}
""",

    'frontend/src/components/layout/AppLayout.tsx': """import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNav from './TopNav';

export default function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
""",

    'frontend/src/components/layout/Sidebar.tsx': """import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Activity, AlertTriangle, Database, MapPin, BarChart3, TestTube } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'States', path: '/states', icon: MapPin },
  { name: 'Parameters', path: '/parameters', icon: TestTube },
  { name: 'Exceedances', path: '/exceedances', icon: Activity },
  { name: 'GIS Map', path: '/map', icon: Map },
  { name: 'Extreme Values', path: '/extremes', icon: AlertTriangle },
  { name: 'Data Quality', path: '/data-quality', icon: Database },
];

export default function Sidebar() {
  return (
    <div className="hidden md:flex flex-col w-64 bg-surface border-r border-slate-700">
      <div className="h-16 flex items-center px-6 border-b border-slate-700">
        <Database className="w-6 h-6 text-primary mr-3" />
        <span className="text-lg font-bold text-white tracking-tight">Groundwater IQ</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive 
                      ? 'bg-primary/10 text-primary' 
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  )
                }
              >
                <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
""",

    'frontend/src/components/layout/TopNav.tsx': """import { Menu } from 'lucide-react';

export default function TopNav() {
  return (
    <header className="h-16 bg-surface border-b border-slate-700 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      <div className="flex items-center md:hidden">
        <button className="text-slate-400 hover:text-white">
          <Menu className="w-6 h-6" />
        </button>
        <span className="ml-3 text-lg font-bold text-white">Groundwater IQ</span>
      </div>
      <div className="flex-1" />
      <div className="flex items-center">
        <span className="text-sm text-slate-400">Phase 7 Foundation</span>
      </div>
    </header>
  );
}
""",

    'frontend/src/pages/Dashboard.tsx': """import { useOverview, useCategories } from '../hooks/useWawqi';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { Card } from '../components/ui/Card';
import { CategoryBadge } from '../components/ui/Badge';

export default function Dashboard() {
  const { data: overviewResp, isLoading: isLoadingOverview, error: errorOverview } = useOverview();
  const { data: catResp, isLoading: isLoadingCat, error: errorCat } = useCategories();

  if (isLoadingOverview || isLoadingCat) return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-64" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    </div>
  );

  if (errorOverview || errorCat) return <ErrorState message="Failed to load dashboard data." />;

  const stats = overviewResp?.data;
  const categories = catResp?.data || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">National Overview</h1>
        <p className="mt-1 text-sm text-slate-400">Phase 5 WAWQI Analytics Baseline</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Total Samples" value={stats?.total_samples?.toLocaleString() || 0} />
        <StatCard title="Eligible for WAWQI" value={stats?.eligible_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Unavailable" value={stats?.unavailable_samples?.toLocaleString() || 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-medium text-white mb-4">Category Distribution</h3>
          <div className="space-y-4">
            {categories.map((c: any) => (
              <div key={c.category} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CategoryBadge category={c.category} />
                  <span className="text-sm text-slate-400">{c.percentage}%</span>
                </div>
                <span className="text-sm font-medium text-white">{c.count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </Card>
        
        <Card>
          <h3 className="text-lg font-medium text-white mb-4">WQI Statistics</h3>
          <div className="space-y-4">
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-400">Median</span>
              <span className="text-white font-medium">{stats?.median_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-400">Mean</span>
              <span className="text-white font-medium">{stats?.mean_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-400">95th Percentile</span>
              <span className="text-white font-medium">{stats?.p95_wqi}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-400">99th Percentile</span>
              <span className="text-white font-medium">{stats?.p99_wqi}</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-slate-400">Max Observation</span>
              <span className="text-white font-medium">{stats?.max_wqi}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
""",

    'frontend/src/pages/StatesOverview.tsx': """import { useStates } from '../hooks/useWawqi';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';
import { Card } from '../components/ui/Card';

export default function StatesOverview() {
  const { data: resp, isLoading, error } = useStates();

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message="Failed to load states." />;
  if (!resp?.data || resp.data.length === 0) return <EmptyState message="No state data found." />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-tight">States Overview</h1>
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-700">
            <thead>
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">State</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Samples</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Eligible</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Median WQI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {resp.data.map((state: any) => (
                <tr key={state.state} className="hover:bg-slate-800/50">
                  <td className="px-3 py-4 text-sm font-medium text-white">{state.state}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.total_samples?.toLocaleString()}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.eligible_samples?.toLocaleString()}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{state.median_wqi}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
""",

    'frontend/src/pages/MapPage.tsx': """import { Card } from '../components/ui/Card';

export default function MapPage() {
  return (
    <div className="space-y-6 h-[calc(100vh-8rem)]">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">GIS Analysis</h1>
        <p className="mt-1 text-sm text-slate-400">Map Foundation established. Leaflet ready.</p>
      </div>
      <Card className="h-full flex items-center justify-center border-slate-700 bg-slate-800/50">
        <div className="text-center">
          <p className="text-slate-400">Leaflet CSS is imported.</p>
          <p className="text-slate-500 text-sm mt-2">Phase 8 will implement full React-Leaflet MapContainer here.</p>
        </div>
      </Card>
    </div>
  );
}
""",

    'frontend/src/pages/StateDetail.tsx': """export default function StateDetail() { return <div className="text-white">State Detail (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/DistrictDetail.tsx': """export default function DistrictDetail() { return <div className="text-white">District Detail (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/Parameters.tsx': """export default function Parameters() { return <div className="text-white">Parameters (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/Exceedances.tsx': """export default function Exceedances() { return <div className="text-white">Exceedances (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/Extremes.tsx': """export default function Extremes() { return <div className="text-white">Extreme Values (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/DataQuality.tsx': """export default function DataQuality() { return <div className="text-white">Data Quality (Phase 8 Placeholder)</div>; }""",
    'frontend/src/pages/NotFound.tsx': """export default function NotFound() { return <div className="text-white">404 - Not Found</div>; }""",

}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)

print("Frontend files generated successfully.")
