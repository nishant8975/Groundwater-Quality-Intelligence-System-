import { useParams, useSearchParams, Link } from 'react-router-dom';
import { useDistrictDetail } from '../hooks/useWawqi';
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

export default function DistrictDetail() {
  const { district } = useParams<{ district: string }>();
  const [searchParams] = useSearchParams();
  const state = searchParams.get('state') || undefined;

  const decodedDistrict = decodeURIComponent(district || '');
  
  const { data: resp, isLoading, error } = useDistrictDetail(decodedDistrict, state);

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message="Failed to load district data." />;

  const d = resp?.data?.[0] || {}; // Backend may return array

  const categoryData = [
    { category: 'Excellent', count: d.c_exc },
    { category: 'Good', count: d.c_good },
    { category: 'Poor', count: d.c_poor },
    { category: 'Very Poor', count: d.c_vpoor },
    { category: 'Unsuitable', count: d.c_uns }
  ];

  return (
    <div className="space-y-6">
      <div>
        <Link to="/districts" className="text-sm text-slate-400 hover:text-white underline mb-4 inline-block">&larr; Back to Districts</Link>
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{decodedDistrict} Analytics</h1>
            <p className="mt-1 text-sm text-slate-400">{d.state}</p>
          </div>
          <div className="flex gap-2">
            <Link 
              to={`/stations?search=${encodeURIComponent(decodedDistrict)}`} 
              className="px-4 py-2 bg-sky-700 hover:bg-sky-600 text-white rounded text-sm font-medium transition-colors"
            >
              View Stations
            </Link>
            <Link 
              to={`/map?district=${encodeURIComponent(decodedDistrict)}${d.state ? `&state=${encodeURIComponent(d.state)}` : ''}`} 
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition-colors"
            >
              View on Map
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Samples" value={d.total_samples?.toLocaleString() || 0} />
        <StatCard title="WAWQI Available" value={d.eligible_samples?.toLocaleString() || 0} />
        <StatCard title="Median WQI" value={d.median_wqi || 0} />
        <StatCard title="Mean WQI" value={d.mean_wqi || 0} />
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
    </div>
  );
}
