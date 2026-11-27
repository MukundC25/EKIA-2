import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import Debugger from './pages/Debugger';
import GraphExplorer from './pages/GraphExplorer';
import History from './pages/History';
import { getHealth } from './services/api';
import './index.css';

export default function App() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    const refresh = () =>
      getHealth()
        .then(setHealth)
        .catch(() => setHealth({ status: 'offline', services: {} }));
    refresh();
    const id = setInterval(refresh, 15000); // keep service badges live
    return () => clearInterval(id);
  }, []);

  return (
    <BrowserRouter>
      <Sidebar health={health} />
      <Routes>
        <Route path="/" element={<Debugger />} />
        <Route path="/graph" element={<GraphExplorer />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </BrowserRouter>
  );
}
