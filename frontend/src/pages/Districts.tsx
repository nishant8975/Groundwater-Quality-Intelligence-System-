import { useSearchParams } from 'react-router-dom';
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
