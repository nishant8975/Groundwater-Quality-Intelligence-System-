import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useStations } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';
import { Search, AlertTriangle, CheckCircle2, SlidersHorizontal, ArrowUpDown } from 'lucide-react';

export default function Stations() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get('page') || '1', 10);
  const search = searchParams.get('search') || '';
  const dataQuality = searchParams.get('data_quality') || '';
  const sortBy = searchParams.get('sort_by') || 'sample_count';
  const order = searchParams.get('order') || 'desc';

  const [searchInput, setSearchInput] = useState(search);

  const { data: resp, isLoading, error } = useStations({ 
    page, 
    limit: 50, 
    search: search.trim(),
    data_quality: dataQuality,
    sort_by: sortBy,
    order: order
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchParams(prev => {
      if (searchInput) prev.set('search', searchInput);
      else prev.delete('search');
      prev.set('page', '1');
      return prev;
    });
  };

  const updateParam = (key: string, value: string) => {
    setSearchParams(prev => {
      if (value) prev.set(key, value);
      else prev.delete(key);
      prev.set('page', '1');
      return prev;
    });
  };

  const handleNextPage = () => {
    setSearchParams(prev => { prev.set('page', (page + 1).toString()); return prev; });
  };

  const handlePrevPage = () => {
    setSearchParams(prev => { prev.set('page', Math.max(1, page - 1).toString()); return prev; });
  };

  const getWqiColorClass = (wqi: number | null) => {
    if (wqi === null || wqi === undefined) return 'text-slate-400 bg-slate-800 border-slate-700';
    if (wqi <= 25) return 'text-emerald-400 bg-emerald-950/60 border-emerald-800/80';
    if (wqi <= 50) return 'text-cyan-400 bg-cyan-950/60 border-cyan-800/80';
    if (wqi <= 75) return 'text-amber-400 bg-amber-950/60 border-amber-800/80';
    if (wqi <= 100) return 'text-orange-400 bg-orange-950/60 border-orange-800/80';
    return 'text-rose-400 bg-rose-950/60 border-rose-800/80';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          Station Intelligence
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Descriptive station-level groundwater quality metrics, sampling eligibility, historical statistics, and data quality classification.
        </p>
      </div>

      <Card>
        {/* Filter Controls Bar */}
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center mb-6">
          <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search station, district, state..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-primary"
            />
          </form>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300">
              <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
              <span>Quality:</span>
              <select
                value={dataQuality}
                onChange={(e) => updateParam('data_quality', e.target.value)}
                className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
              >
                <option value="" className="bg-slate-900">All Stations</option>
                <option value="DATA_RICH" className="bg-slate-900">Data Rich Only</option>
                <option value="DATA_LIMITED" className="bg-slate-900">Data Limited Only</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-300">
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
              <span>Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => updateParam('sort_by', e.target.value)}
                className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
              >
                <option value="sample_count" className="bg-slate-900">Sample Count</option>
                <option value="wawqi_eligibility_percentage" className="bg-slate-900">Eligibility %</option>
                <option value="median_wqi" className="bg-slate-900">Median WAWQI</option>
                <option value="station_name" className="bg-slate-900">Station Name</option>
              </select>
            </div>

            <button
              onClick={() => updateParam('order', order === 'asc' ? 'desc' : 'asc')}
              className="px-3 py-1.5 bg-slate-900 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium transition-colors"
            >
              {order === 'asc' ? '↑ Asc' : '↓ Desc'}
            </button>
          </div>
        </div>

        {/* Results Info & Pagination */}
        <div className="flex justify-between items-center text-xs text-slate-400 mb-4 pb-2 border-b border-slate-800">
          <span>
            {resp?.pagination ? `Showing Page ${page} of ${resp.pagination.totalPages} (${resp.pagination.total.toLocaleString()} stations total)` : 'Loading stations...'}
          </span>
          {resp?.pagination && (
            <div className="flex gap-2">
              <button
                onClick={handlePrevPage}
                disabled={page <= 1}
                className="px-3 py-1 bg-slate-800 text-white rounded disabled:opacity-40 hover:bg-slate-700 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={handleNextPage}
                disabled={page >= resp.pagination.totalPages}
                className="px-3 py-1 bg-slate-800 text-white rounded disabled:opacity-40 hover:bg-slate-700 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Table Content */}
        {isLoading ? (
          <Skeleton className="h-96 w-full" />
        ) : error ? (
          <ErrorState message="Failed to load station intelligence dataset." />
        ) : resp?.data?.length === 0 ? (
          <EmptyState message="No stations match the search/filter criteria." />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Station Identity</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Location</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">Samples</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">WAWQI Eligibility</th>
                  <th className="px-3 py-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">Median WAWQI</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Dominant Contaminant</th>
                  <th className="px-3 py-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">Data Quality</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {resp?.data.map((st: any) => (
                  <tr key={st.station_hash} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-3 py-3 text-sm">
                      <Link 
                        to={`/stations/${st.station_hash}`}
                        className="font-semibold text-sky-400 hover:text-sky-300 hover:underline block max-w-[200px] truncate"
                        title={st.station_name}
                      >
                        {st.station_name}
                      </Link>
                    </td>
                    <td className="px-3 py-3 text-xs text-slate-300">
                      <span className="font-medium text-slate-200">{st.district}</span>
                      <span className="text-slate-500 text-[11px] block">{st.state}</span>
                    </td>
                    <td className="px-3 py-3 text-sm text-right font-mono text-slate-200">
                      {st.sample_count}
                    </td>
                    <td className="px-3 py-3 text-xs text-slate-300 min-w-[130px]">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="font-mono text-slate-200">{st.wawqi_eligibility_percentage}%</span>
                        <span className="text-[10px] text-slate-500">({st.wawqi_available_count}/{st.sample_count})</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${st.wawqi_eligibility_percentage >= 50 ? 'bg-sky-500' : 'bg-amber-500'}`}
                          style={{ width: `${Math.min(100, Math.max(0, st.wawqi_eligibility_percentage))}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-3 py-3 text-center">
                      {st.median_wqi !== null ? (
                        <span className={`inline-block px-2 py-0.5 text-xs font-bold font-mono rounded border ${getWqiColorClass(st.median_wqi)}`}>
                          {parseFloat(st.median_wqi).toFixed(1)}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-600 font-mono">N/A</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-xs text-slate-300">
                      {st.historically_dominant_parameters?.length ? (
                        <div className="flex flex-wrap gap-1">
                          {st.historically_dominant_parameters.map((p: string) => (
                            <span key={p} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px] uppercase">
                              {p}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-600">None</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-center">
                      {st.data_quality_class === 'DATA RICH' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                          <CheckCircle2 className="w-3 h-3" /> DATA RICH
                        </span>
                      ) : (
                        <span 
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60 cursor-help"
                          title={st.data_quality_reason}
                        >
                          <AlertTriangle className="w-3 h-3" /> DATA LIMITED
                        </span>
                      )}
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
