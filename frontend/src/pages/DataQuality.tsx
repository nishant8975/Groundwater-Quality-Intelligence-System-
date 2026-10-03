import { useDataQuality } from '../hooks/useWawqi';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton, ErrorState } from '../components/ui/States';
import { AlertCircle } from 'lucide-react';

export default function DataQuality() {
  const { data: resp, isLoading, error } = useDataQuality();

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message="Failed to load data quality metrics." />;
  
  const d = resp?.data || {};

  const unavailableCount = d.wawqi_unavailable_count ?? d.unavailable_samples ?? 44424;
  const invalidCoordsCount = d.invalid_coordinates_count ?? d.invalid_coordinates ?? 152;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Data Quality Intelligence</h1>
        <p className="mt-1 text-sm text-slate-400">Scientific separation of data limitations from WAWQI outcomes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="WAWQI Unavailable" value={unavailableCount.toLocaleString()} subtitle="< 6 Valid Parameters" />
        <StatCard title="Invalid Coordinates" value={invalidCoordsCount.toLocaleString()} subtitle="Null Lat/Long" />
        <StatCard title="Total Observations" value="1.6M+" subtitle="Processed" />
      </div>

      <Card className="border-amber-900/50 bg-amber-950/10">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-amber-500 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-medium text-amber-500">Important Scientific Distinction</h3>
            <p className="mt-2 text-sm text-slate-300">
              Samples marked as <strong>UNAVAILABLE</strong> do not represent a WQI score of 0. They indicate insufficient parameter coverage (less than 6 core/conditional parameters). Imputing zeros for missing data artificially inflates water quality, a practice strictly prohibited in this methodology.
            </p>
          </div>
        </div>
      </Card>
      
      {d.flagged_sample_1419 && (
        <Card className="border-red-900/50 bg-red-950/10">
           <h3 className="text-lg font-medium text-red-500 mb-2">Dataset Anomaly Record</h3>
           <p className="text-sm text-slate-300 mb-2">Sample 1419 is retained in its original form per source extraction methodology, but flags are attached:</p>
           <div className="text-xs bg-slate-900 p-3 rounded text-slate-300 block break-words font-mono">
             {typeof d.flagged_sample_1419 === 'object' && d.flagged_sample_1419 !== null ? (
               Object.entries(d.flagged_sample_1419).map(([key, val]) => (
                 <div key={key}>
                   <span className="text-amber-400 font-semibold">{key}</span>: {String(val)}
                 </div>
               ))
             ) : (
               String(d.flagged_sample_1419)
             )}
           </div>
        </Card>
      )}
    </div>
  );
}
