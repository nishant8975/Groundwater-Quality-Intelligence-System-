import { useOverview, useCategories, useStates } from '../hooks/useWawqi';
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

  // Transform state data for Recharts stacked bar chart
  const topStatesChartData = states.slice(0, 10).map((s: any) => ({
    state: s.state,
    excellent: parseFloat(s.excellent_count || s.c_exc || '0'),
    good: parseFloat(s.good_count || s.c_good || '0'),
    poor: parseFloat(s.poor_count || s.c_poor || '0'),
    very_poor: parseFloat(s.very_poor_count || s.c_vpoor || '0'),
    unsuitable: parseFloat(s.unsuitable_count || s.c_uns || '0')
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Groundwater Quality Intelligence</h1>
        <p className="mt-1 text-slate-400">Analytics Dashboard - National Overview</p>
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
          <p className="text-sm text-slate-400 mb-6">Display range 0–300. Values above 300 exist (&gt;300 bin). This visualization prevents unsuitably high extreme tails from breaking scale readability.</p>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="bin" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" />
                <Tooltip 
                  cursor={{ fill: '#1E293B' }} 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '0.375rem', color: '#F8FAFC' }}
                  itemStyle={{ color: '#F8FAFC' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
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
              <span className="text-white font-medium">{stats?.min_wqi != null ? Number(stats.min_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">Median</span>
              <span className="text-white font-medium">{stats?.median_wqi != null ? Number(stats.median_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">Mean</span>
              <span className="text-white font-medium">{((stats as any)?.avg_wqi ?? stats?.mean_wqi) != null ? Number((stats as any)?.avg_wqi ?? stats?.mean_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">75th Percentile</span>
              <span className="text-white font-medium">{stats?.p75_wqi != null ? Number(stats.p75_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">95th Percentile</span>
              <span className="text-white font-medium">{stats?.p95_wqi != null ? Number(stats.p95_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-700 pb-2">
              <span className="text-slate-300">99th Percentile</span>
              <span className="text-white font-medium">{stats?.p99_wqi != null ? Number(stats.p99_wqi).toFixed(2) : '-'}</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-slate-300">Maximum</span>
              <span className="text-white font-medium text-red-400">{stats?.max_wqi != null ? Number(stats.max_wqi).toFixed(2) : '-'}</span>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-medium text-white mb-2">State Category Composition</h3>
        <p className="text-sm text-slate-400 mb-6">Showing top 10 states by total sample volume.</p>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topStatesChartData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
              <XAxis type="number" stroke="#94A3B8" />
              <YAxis dataKey="state" type="category" stroke="#94A3B8" width={120} tick={{fontSize: 12}} />
              <Tooltip 
                cursor={{ fill: '#1E293B' }} 
                contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '0.375rem', color: '#F8FAFC' }}
                itemStyle={{ color: '#F8FAFC' }}
                labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
              />
              <Legend />
              <Bar dataKey="excellent" name="Excellent" stackId="a" fill={CATEGORY_COLORS['Excellent']} />
              <Bar dataKey="good" name="Good" stackId="a" fill={CATEGORY_COLORS['Good']} />
              <Bar dataKey="poor" name="Poor" stackId="a" fill={CATEGORY_COLORS['Poor']} />
              <Bar dataKey="very_poor" name="Very Poor" stackId="a" fill={CATEGORY_COLORS['Very Poor']} />
              <Bar dataKey="unsuitable" name="Unsuitable" stackId="a" fill={CATEGORY_COLORS['Unsuitable']} />
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
                const totalSamples = parseInt(s.total_samples || '0', 10);
                const eligibleSamples = parseInt(s.eligible_samples || s.available || '0', 10);
                const unavailableSamples = parseInt(s.unavailable_samples || s.unavailable || '0', 10);
                const medianWqi = s.median_wqi !== undefined && s.median_wqi !== null ? parseFloat(s.median_wqi).toFixed(2) : '-';
                const meanWqi = (s.avg_wqi ?? s.mean_wqi) !== undefined && (s.avg_wqi ?? s.mean_wqi) !== null ? parseFloat(s.avg_wqi ?? s.mean_wqi).toFixed(2) : '-';

                const excPct = s.excellent_pct !== undefined && s.excellent_pct !== null 
                  ? parseFloat(s.excellent_pct).toFixed(1) 
                  : (eligibleSamples > 0 ? ((parseFloat(s.excellent_count || s.c_exc || '0') / eligibleSamples) * 100).toFixed(1) : '0.0');
                const goodPct = s.good_pct !== undefined && s.good_pct !== null 
                  ? parseFloat(s.good_pct).toFixed(1) 
                  : (eligibleSamples > 0 ? ((parseFloat(s.good_count || s.c_good || '0') / eligibleSamples) * 100).toFixed(1) : '0.0');
                const poorPct = s.poor_pct !== undefined && s.poor_pct !== null 
                  ? parseFloat(s.poor_pct).toFixed(1) 
                  : (eligibleSamples > 0 ? ((parseFloat(s.poor_count || s.c_poor || '0') / eligibleSamples) * 100).toFixed(1) : '0.0');
                const vpoorPct = s.very_poor_pct !== undefined && s.very_poor_pct !== null 
                  ? parseFloat(s.very_poor_pct).toFixed(1) 
                  : (eligibleSamples > 0 ? ((parseFloat(s.very_poor_count || s.c_vpoor || '0') / eligibleSamples) * 100).toFixed(1) : '0.0');
                const unsPct = s.unsuitable_pct !== undefined && s.unsuitable_pct !== null 
                  ? parseFloat(s.unsuitable_pct).toFixed(1) 
                  : (eligibleSamples > 0 ? ((parseFloat(s.unsuitable_count || s.c_uns || '0') / eligibleSamples) * 100).toFixed(1) : '0.0');

                return (
                  <tr key={s.state} className="hover:bg-slate-800/50">
                    <td className="px-3 py-4 text-sm font-medium text-white">{s.state}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{totalSamples.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{eligibleSamples.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{unavailableSamples.toLocaleString()}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{medianWqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{meanWqi}</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{excPct}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{goodPct}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{poorPct}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{vpoorPct}%</td>
                    <td className="px-3 py-4 text-sm text-slate-300 text-right">{unsPct}%</td>
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
