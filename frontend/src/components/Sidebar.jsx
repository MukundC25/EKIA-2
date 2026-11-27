import { NavLink } from 'react-router-dom';
import { Bug, Network, History, Terminal, Cpu, Share2, Clock, Activity } from 'lucide-react';

const navItems = [
  { path: '/',       icon: Bug,     label: 'Debugger' },
  { path: '/graph',  icon: Network, label: 'Knowledge Graph' },
  { path: '/history',icon: History, label: 'History' },
];

const SERVICE_MAP = {
  rag:   { label: 'Vector DB',   icon: <Share2 size={12} /> },
  graph: { label: 'Neo4j Graph', icon: <Network size={12} /> },
  llm:   { label: 'Groq LLM',  icon: <Cpu size={12} /> },
  langfuse: { label: 'Langfuse',  icon: <Activity size={12} /> },
};

export default function Sidebar({ health }) {
  const services = health?.services || {};

  const isOnline = (key) => {
    const val = services[key] || '';
    return val === 'connected' || val === 'ready';
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="sidebar-icon-box">
            <Terminal size={17} color="#fff" strokeWidth={2.5} />
          </div>
          <div>
            <div className="sidebar-title">EKIA-2</div>
            <div className="sidebar-subtitle">AI Debugger</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-section-label">Navigation</div>
      <nav className="sidebar-nav">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon"><Icon size={15} strokeWidth={2} /></span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer — Services */}
      <div className="sidebar-footer">
        <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.6px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
          Services
        </div>
        {Object.entries(SERVICE_MAP).map(([key, { label, icon }]) => (
          <div className="service-status-row" key={key}>
            <div className="service-status-label">
              <span style={{ color: 'var(--text-muted)' }}>{icon}</span>
              <span>{label}</span>
            </div>
            <span className={`status-badge ${isOnline(key) ? 'online' : 'offline'}`}>
              {isOnline(key) ? 'online' : 'offline'}
            </span>
          </div>
        ))}
        <div className="sidebar-version">
          <div className="pulse-dot" />
          <span>EKIA-2 v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
