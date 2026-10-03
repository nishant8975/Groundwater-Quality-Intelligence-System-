import { useParams, Link } from 'react-router-dom';
import { useStationDetail } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { Skeleton, ErrorState, EmptyState } from '../components/ui/States';
import { CategoryBadge } from '../components/ui/Badge';
import { ArrowLeft, AlertTriangle, CheckCircle2, Calendar, Activity, MapPin, TestTube2, Info } from 'lucide-react';

const PARAM_STANDARDS: Record<string, { label: string; unit: string; standard: string }> = {
  ph: { label: 'pH', unit: 'pH', standard: '6.5 - 8.5' },
  chloride: { label: 'Chloride', unit: 'mg/L', standard: '250' },
  sulphate: { label: 'Sulphate', unit: 'mg/L', standard: '200' },
  hardness: { label: 'Hardness', unit: 'mg/L', standard: '200' },
  calcium: { label: 'Calcium', unit: 'mg/L', standard: '75' },
  magnesium: { label: 'Magnesium', unit: 'mg/L', standard: '30' },
  iron: { label: 'Iron', unit: 'mg/L', standard: '0.3' },
  arsenic: { label: 'Arsenic', unit: 'mg/L', standard: '0.01' },
  uranium: { label: 'Uranium', unit: 'mg/L', standard: '0.03' }
};

export default function StationDetail() {
  const { hash } = useParams<{ hash: string }>();
  const { data: resp, isLoading, error } = useStationDetail(hash || '');

  const station = resp?.data;

  const getWqiColorClass = (wqi: number | null) => {
    if (wqi === null || wqi === undefined) return 'text-slate-400 bg-slate-800 border-slate-700';
    if (wqi <= 25) return 'text-emerald-400 bg-emerald-950/60 border-emerald-800/80';
    if (wqi <= 50) return 'text-cyan-400 bg-cyan-950/60 border-cyan-800/80';
    if (wqi <= 75) return 'text-amber-400 bg-amber-950/60 border-amber-800/80';
    if (wqi <= 100) return 'text-orange-400 bg-orange-950/60 border-orange-800/80';
    return 'text-rose-400 bg-rose-950/60 border-rose-800/80';
  };

  if (isLoading) return <div className="space-y-6"><Skeleton className="h-48 w-full" /><Skeleton className="h-96 w-full" /></div>;
  if (error || !station) return <ErrorState message="Station detail not found." />;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Navigation */}
      <div>
        <Link 
          to="/stations"
          className="inline-flex items-center text-xs font-semibold text-sky-400 hover:text-sky-300 transition-colors mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to Stations Directory
        </Link>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              {station.station_name}
            </h1>
            <p className="mt-1 text-sm text-slate-400 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-slate-500" />
              <span>{station.district}, {station.state}</span>
              <span className="text-slate-600">•</span>
              <span className="font-mono text-xs text-slate-500">
                {parseFloat(station.latitude).toFixed(4)}°N, {parseFloat(station.longitude).toFixed(4)}°E
              </span>
            </p>
          </div>

          <div>
            {station.data_quality_class === 'DATA RICH' ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
                <CheckCircle2 className="w-4 h-4" /> DATA RICH STATION
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-950/80 text-amber-400 border border-amber-800/80">
                <AlertTriangle className="w-4 h-4" /> DATA LIMITED STATION
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Data Quality Warning Alert */}
      {station.data_quality_class === 'DATA LIMITED' && (
        <div className="p-4 rounded-lg bg-amber-950/40 border border-amber-800/60 text-amber-200 text-xs leading-relaxed flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-amber-300 block text-sm mb-0.5">⚠ DATA LIMITED CLASSIFICATION NOTICE</span>
            <span>{station.data_quality_reason}</span> This station's statistical profile should be interpreted with caution as limited historical depth may distort overall trends.
          </div>
        </div>
      )}

      {/* Source Data Warnings Alert */}
      {station.latest_source_warning && (
        <div className="p-4 rounded-lg bg-slate-900 border border-amber-700/50 text-slate-300 text-xs leading-relaxed flex items-start gap-3">
          <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-amber-300 block text-sm mb-0.5">Source Measurement Quality Flag</span>
            <span className="font-mono text-amber-200">{station.latest_source_warning}</span>
          </div>
        </div>
      )}

      {/* Key Metric Summary Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Sample History */}
        <Card className="p-4">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
            <span>Historical Samples</span>
            <Calendar className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-2">
            {station.sample_count}
          </div>
          <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-2 flex justify-between">
            <span>First: {station.first_sample_date ? new Date(station.first_sample_date).getFullYear() : 'N/A'}</span>
            <span>Latest: {station.last_sample_date ? new Date(station.last_sample_date).getFullYear() : 'N/A'}</span>
          </div>
        </Card>

        {/* Card 2: WAWQI Eligibility */}
        <Card className="p-4">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
            <span>WAWQI Eligibility</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mb-2">
            {station.wawqi_eligibility_percentage}%
          </div>
          <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-2 flex justify-between">
            <span>Available: {station.wawqi_available_count}</span>
            <span>Unavailable: {station.wawqi_unavailable_count}</span>
          </div>
        </Card>

        {/* Card 3: Median & P90 WAWQI */}
        <Card className="p-4">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
            <span>Median WAWQI</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-2xl font-bold font-mono text-white">
              {station.median_wqi !== null ? parseFloat(station.median_wqi).toFixed(1) : 'N/A'}
            </span>
            {station.median_wqi !== null && (
              <span className={`text-xs px-1.5 py-0.5 rounded font-semibold border ${getWqiColorClass(station.median_wqi)}`}>
                {station.median_wqi <= 25 ? 'Excellent' : station.median_wqi <= 50 ? 'Good' : station.median_wqi <= 75 ? 'Poor' : station.median_wqi <= 100 ? 'V. Poor' : 'Unsuitable'}
              </span>
            )}
          </div>
          <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-2 flex justify-between">
            <span>90th Pct: {station.p90_wqi !== null ? parseFloat(station.p90_wqi).toFixed(1) : 'N/A'}</span>
            <span>Max: {station.max_wqi !== null ? parseFloat(station.max_wqi).toFixed(1) : 'N/A'}</span>
          </div>
        </Card>

        {/* Card 4: Dominant Contaminant */}
        <Card className="p-4">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
            <span>Dominant Contaminant</span>
            <TestTube2 className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-lg font-bold text-white mb-2 truncate">
            {station.historically_dominant_parameters?.length ? (
              <span className="uppercase text-sky-400">{station.historically_dominant_parameters.join(', ')}</span>
            ) : (
              <span className="text-slate-500">None</span>
            )}
          </div>
          <div className="text-[11px] text-slate-400 border-t border-slate-800 pt-2 flex justify-between">
            <span>Frequency:</span>
            <span className="font-mono text-slate-200">{station.dominant_parameter_percentage}% of valid samples</span>
          </div>
        </Card>
      </div>

      {/* WAWQI Category Breakdown Pills */}
      <Card>
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">WAWQI Historical Category Distribution</h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="p-3 bg-emerald-950/30 border border-emerald-800/40 rounded-lg text-center">
            <span className="text-xs text-emerald-400 font-semibold block">Excellent</span>
            <span className="text-xl font-bold font-mono text-emerald-300">{station.excellent_count}</span>
          </div>
          <div className="p-3 bg-cyan-950/30 border border-cyan-800/40 rounded-lg text-center">
            <span className="text-xs text-cyan-400 font-semibold block">Good</span>
            <span className="text-xl font-bold font-mono text-cyan-300">{station.good_count}</span>
          </div>
          <div className="p-3 bg-amber-950/30 border border-amber-800/40 rounded-lg text-center">
            <span className="text-xs text-amber-400 font-semibold block">Poor</span>
            <span className="text-xl font-bold font-mono text-amber-300">{station.poor_count}</span>
          </div>
          <div className="p-3 bg-orange-950/30 border border-orange-800/40 rounded-lg text-center">
            <span className="text-xs text-orange-400 font-semibold block">Very Poor</span>
            <span className="text-xl font-bold font-mono text-orange-300">{station.very_poor_count}</span>
          </div>
          <div className="p-3 bg-rose-950/30 border border-rose-800/40 rounded-lg text-center col-span-2 sm:col-span-1">
            <span className="text-xs text-rose-400 font-semibold block">Unsuitable</span>
            <span className="text-xl font-bold font-mono text-rose-300">{station.unsuitable_count}</span>
          </div>
        </div>
      </Card>

      {/* Station Parameter Statistical Profile Table */}
      <Card>
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Parameter Statistical Profile</h3>
        {station.parameters?.length === 0 ? (
          <EmptyState message="No parameter observations available." />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-800">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Parameter</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Obs. Count</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Min</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Median</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Max</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">P75</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">P90</th>
                  <th className="px-3 py-3 text-center text-xs font-semibold text-slate-400 uppercase">Standard Limit</th>
                  <th className="px-3 py-3 text-right text-xs font-semibold text-slate-400 uppercase">Exceedance %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {station.parameters?.map((p: any) => {
                  const meta = PARAM_STANDARDS[p.parameter] || { label: p.parameter, unit: '', standard: 'N/A' };
                  const excPct = parseFloat(p.exceedance_percentage || 0);
                  return (
                    <tr key={p.parameter} className="hover:bg-slate-800/40">
                      <td className="px-3 py-3 text-sm font-medium text-white">
                        {meta.label} <span className="text-xs text-slate-500 font-normal">({meta.unit})</span>
                      </td>
                      <td className="px-3 py-3 text-xs font-mono text-right text-slate-300">{p.observation_count}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right text-slate-300">{p.minimum !== null ? parseFloat(p.minimum).toFixed(2) : 'N/A'}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right font-semibold text-slate-100">{p.median !== null ? parseFloat(p.median).toFixed(2) : 'N/A'}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right text-slate-300">{p.maximum !== null ? parseFloat(p.maximum).toFixed(2) : 'N/A'}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right text-slate-400">{p.p75 !== null ? parseFloat(p.p75).toFixed(2) : 'N/A'}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right text-slate-400">{p.p90 !== null ? parseFloat(p.p90).toFixed(2) : 'N/A'}</td>
                      <td className="px-3 py-3 text-xs text-center text-slate-400 font-mono">{meta.standard}</td>
                      <td className="px-3 py-3 text-xs font-mono text-right">
                        {excPct > 0 ? (
                          <span className="font-bold text-amber-400 bg-amber-950/50 px-1.5 py-0.5 rounded border border-amber-800/60">
                            {excPct}% ({p.exceedance_count})
                          </span>
                        ) : (
                          <span className="text-slate-500">0%</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Historical Sample Timeline Table */}
      <Card>
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Sample History Timeline ({station.history?.length || 0} samples)</h3>
        {station.history?.length === 0 ? (
          <EmptyState message="No historical samples available for this station." />
        ) : (
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="sticky top-0 bg-slate-900 shadow">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Sample ID</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Sample Date</th>
                  <th className="px-3 py-3 text-center text-xs font-semibold text-slate-400 uppercase">WAWQI Score</th>
                  <th className="px-3 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Category</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {station.history?.map((h: any) => (
                  <tr key={h.sample_id} className="hover:bg-slate-800/40">
                    <td className="px-3 py-3 text-xs font-mono text-slate-400">#{h.sample_id}</td>
                    <td className="px-3 py-3 text-xs text-slate-200">
                      {h.sample_date ? new Date(h.sample_date).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-3 py-3 text-center">
                      {h.wqi !== null ? (
                        <span className={`inline-block px-2 py-0.5 text-xs font-bold font-mono rounded border ${getWqiColorClass(h.wqi)}`}>
                          {parseFloat(h.wqi).toFixed(1)}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-600 font-mono">UNAVAILABLE</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-xs">
                      <CategoryBadge category={h.category} />
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
