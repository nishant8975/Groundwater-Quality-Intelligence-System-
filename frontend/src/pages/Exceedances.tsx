import { useSearchParams } from 'react-router-dom';
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
