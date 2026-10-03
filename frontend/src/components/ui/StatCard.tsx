import { Card } from './Card';
import React from 'react';

export function StatCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <Card>
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">{title}</h3>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-semibold text-white">{value}</span>
        {subtitle && <span className="text-sm text-slate-400">{subtitle}</span>}
      </div>
    </Card>
  );
}
