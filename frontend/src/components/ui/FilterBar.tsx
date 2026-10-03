import { useSearchParams } from 'react-router-dom';

interface FilterConfig {
  showState?: boolean;
  showDistrict?: boolean;
  showCategory?: boolean;
  showParameter?: boolean;
  statesList?: string[];
  parametersList?: string[];
}

export const FilterBar = ({ config }: { config: FilterConfig }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const handleFilterChange = (key: string, value: string) => {
    setSearchParams(prev => {
      if (value) prev.set(key, value);
      else prev.delete(key);
      if (key === 'state') prev.delete('district'); // reset district on state change
      prev.set('page', '1'); // reset pagination
      return prev;
    });
  };

  const handleReset = () => {
    setSearchParams({});
  };

  return (
    <div className="flex flex-wrap items-center gap-4 bg-slate-800 p-4 rounded border border-slate-700">
      <span className="text-sm font-medium text-slate-300">Filters:</span>
      
      {config.showState && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('state') || ''}
          onChange={e => handleFilterChange('state', e.target.value)}
        >
          <option value="">All States</option>
          {config.statesList?.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      )}

      {config.showDistrict && searchParams.get('state') && (
        <input 
          type="text"
          placeholder="District name..."
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm"
          value={searchParams.get('district') || ''}
          onChange={e => handleFilterChange('district', e.target.value)}
        />
      )}

      {config.showCategory && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('category') || ''}
          onChange={e => handleFilterChange('category', e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="Excellent">Excellent</option>
          <option value="Good">Good</option>
          <option value="Poor">Poor</option>
          <option value="Very Poor">Very Poor</option>
          <option value="Unsuitable">Unsuitable</option>
        </select>
      )}

      {config.showParameter && (
        <select 
          className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm min-w-[150px]"
          value={searchParams.get('parameter') || ''}
          onChange={e => handleFilterChange('parameter', e.target.value)}
        >
          <option value="">All Parameters</option>
          {config.parametersList?.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
        </select>
      )}

      {Array.from(searchParams.keys()).length > 0 && (
        <button 
          onClick={handleReset}
          className="text-sm text-slate-400 hover:text-white underline ml-auto"
        >
          Reset Filters
        </button>
      )}
    </div>
  );
};
