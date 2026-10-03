import { useParameters } from '../hooks/useWawqi';
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
