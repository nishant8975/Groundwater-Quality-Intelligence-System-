import { useState, useEffect } from 'react';
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
