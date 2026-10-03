import { useParams, Link } from 'react-router-dom';
import { useStateDetail, useDistricts } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const CATEGORY_COLORS: Record<string, string> = {
  'Excellent': '#34D399',
  'Good': '#60A5FA',
  'Poor': '#FBBF24',
  'Very Poor': '#F97316',
  'Unsuitable': '#EF4444',
  'UNAVAILABLE': '#64748B'
};

export default function StateDetail() {
  const { state } = useParams<{ state: string }>();
  const decodedState = decodeURIComponent(state || '');
  
  const { data: stateResp, isLoading: isLoadingState, error: errorState } = useStateDetail(decodedState);
  const { data: districtsResp, isLoading: isLoadingDist } = useDistricts({ state: decodedState });

  if (isLoadingState || isLoadingDist) return <Skeleton className="h-96 w-full" />;
  if (errorState) return <ErrorState message="Failed to load state data." />;

  const s = stateResp?.data || {};
  const districts = districtsResp?.data || [];

  const categoryData = [
    { category: 'Excellent', count: s.c_exc },
    { category: 'Good', count: s.c_good },
    { category: 'Poor', count: s.c_poor },
    { category: 'Very Poor', count: s.c_vpoor },
    { category: 'Unsuitable', count: s.c_uns }
  ];

  return (
    <div className="space-y-6">
      <div>
        <Link to="/states" className="text-sm text-slate-400 hover:text-white underline mb-4 inline-block">&larr; Back to States</Link>
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white tracking-tight">{decodedState} Analytics</h1>
          <div className="flex gap-2">
            <Link to={`/stations?search=${encodeURIComponent(decodedState)}`} className="px-4 py-2 bg-sky-700 hover:bg-sky-600 text-white rounded text-sm font-medium transition-colors">
              View Stations
            </Link>
            <Link to={`/map?state=${encodeURIComponent(decodedState)}`} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition-colors">
              View on Map
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Samples" value={s.total_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Available" value={s.eligible_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Unavailable" value={s.unavailable_samples?.toLocaleString() || 0} />
        <StatCard title="Median WQI" value={s.median_wqi || 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-medium text-white mb-6">Category Distribution</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="category" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" />
                <Tooltip cursor={{fill: '#1E293B'}} contentStyle={{backgroundColor: '#0F172A', borderColor: '#334155', color: '#F8FAFC'}} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {categoryData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.category]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-medium text-white mb-4">District Overview</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-700">
            <thead>
              <tr>
                <th className="px-3 py-3 text-left text-xs font-medium text-slate-400 uppercase">District</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Samples</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Median WQI</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Mean WQI</th>
                <th className="px-3 py-3 text-right text-xs font-medium text-slate-400 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {districts.map((d: any) => (
                <tr key={d.district} className="hover:bg-slate-800/50">
                  <td className="px-3 py-4 text-sm font-medium text-white">{d.district}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.total_samples?.toLocaleString()}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.median_wqi}</td>
                  <td className="px-3 py-4 text-sm text-slate-300 text-right">{d.mean_wqi}</td>
                  <td className="px-3 py-4 text-sm text-right">
                    <Link to={`/districts/${encodeURIComponent(d.district)}?state=${encodeURIComponent(decodedState)}`} className="text-blue-400 hover:underline">View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
