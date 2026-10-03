import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Activity, AlertTriangle, Database, MapPin, TestTube, Radio } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Stations', path: '/stations', icon: Radio },
  { name: 'States', path: '/states', icon: MapPin },
  { name: 'Parameters', path: '/parameters', icon: TestTube },
  { name: 'Exceedances', path: '/exceedances', icon: Activity },
  { name: 'GIS Map', path: '/map', icon: Map },
  { name: 'Extreme Values', path: '/extremes', icon: AlertTriangle },
  { name: 'Data Quality', path: '/data-quality', icon: Database },
];

export default function Sidebar() {
  return (
    <div className="hidden md:flex flex-col w-64 bg-surface border-r border-slate-700">
      <div className="h-16 flex items-center px-6 border-b border-slate-700">
        <Database className="w-6 h-6 text-primary mr-3" />
        <span className="text-lg font-bold text-white tracking-tight">Groundwater IQ</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive 
                      ? 'bg-primary/10 text-primary' 
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                  )
                }
              >
                <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
