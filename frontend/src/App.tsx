import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import Stations from './pages/Stations';
import StationDetail from './pages/StationDetail';
import StatesOverview from './pages/StatesOverview';
import StateDetail from './pages/StateDetail';
import Districts from './pages/Districts';
import DistrictDetail from './pages/DistrictDetail';
import Parameters from './pages/Parameters';
import Exceedances from './pages/Exceedances';
import Extremes from './pages/Extremes';
import DataQuality from './pages/DataQuality';
import MapPage from './pages/MapPage';

export default function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/stations" element={<Stations />} />
          <Route path="/stations/:hash" element={<StationDetail />} />
          <Route path="/states" element={<StatesOverview />} />
          <Route path="/states/:state" element={<StateDetail />} />
          <Route path="/districts" element={<Districts />} />
          <Route path="/districts/:district" element={<DistrictDetail />} />
          <Route path="/parameters" element={<Parameters />} />
          <Route path="/exceedances" element={<Exceedances />} />
          <Route path="/extremes" element={<Extremes />} />
          <Route path="/data-quality" element={<DataQuality />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="*" element={
            <div className="flex items-center justify-center h-96">
              <h2 className="text-2xl text-slate-400">404 - Page Not Found</h2>
            </div>
          } />
        </Routes>
      </AppLayout>
    </Router>
  );
}

