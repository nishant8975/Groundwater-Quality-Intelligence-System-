import { useStates } from '../hooks/useWawqi';
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
