import React from 'react';
import { AlertCircle, Database } from 'lucide-react';

export function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-700 rounded ${className}`} />;
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-red-950/20 rounded-lg border border-red-900/50">
      <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-red-400">Error Loading Data</h3>
      <p className="mt-1 text-sm text-red-300/80">{message}</p>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-surface/50 rounded-lg border border-slate-700 border-dashed">
      <Database className="w-12 h-12 text-slate-500 mb-4 opacity-50" />
      <h3 className="text-lg font-medium text-slate-300">No Data Available</h3>
      <p className="mt-1 text-sm text-slate-500">{message}</p>
    </div>
  );
}
