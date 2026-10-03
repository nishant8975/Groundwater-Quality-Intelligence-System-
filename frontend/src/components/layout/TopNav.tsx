import { Menu } from 'lucide-react';

export default function TopNav() {
  return (
    <header className="h-16 bg-surface border-b border-slate-700 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      <div className="flex items-center md:hidden">
        <button className="text-slate-400 hover:text-white">
          <Menu className="w-6 h-6" />
        </button>
        <span className="ml-3 text-lg font-bold text-white">Groundwater IQ</span>
      </div>
      <div className="flex-1" />
      <div className="flex items-center">
      </div>
    </header>
  );
}
