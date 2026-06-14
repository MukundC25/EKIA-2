import { useEffect, useState } from 'react';
import GraphVisualization from '../components/GraphVisualization';
import { getFullGraph, getGraphStats, searchGraph } from '../services/api';
import { Network, RefreshCw, AlertCircle, Search } from 'lucide-react';

const STAT_COLORS = {
  errors:        'var(--color-error)',
  concepts:      'var(--color-info)',
  fixes:         'var(--color-success)',
  problems:      'var(--text-accent)',
  languages:     'var(--color-warning)',
  relationships: 'var(--text-secondary)',
};

export default function GraphExplorer() {
  const [graphData, setGraphData] = useState(null);
  const [stats,     setStats]     = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [isDemo,    setIsDemo]    = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [graph, graphStats] = await Promise.all([getFullGraph(150), getGraphStats()]);
      setGraphData({ nodes: graph.nodes, edges: graph.edges });
      setIsDemo(graph.demo_mode || false);
      setStats(graphStats);
    } catch (e) {
      console.error('Graph load error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || isDemo) return;
    setSearching(true);
    try {
      const results = await searchGraph(searchQuery.trim());
      setSearchResults(results);
    } catch (err) {
      console.error('Graph search error:', err);
      setSearchResults({ results: [], count: 0, query: searchQuery });
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => { load(); }, []);

  const statItems = stats
    ? Object.entries({
        errors:        stats.errors,
        concepts:      stats.concepts,
        fixes:         stats.fixes,
        problems:      stats.problems,
        languages:     stats.languages,
        relationships: stats.relationships,
      })
    : [];

  return (
    <div className="main-content">
      <div className="page-header">
        <div className="page-header-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              className="page-icon-box"
              style={{ background: 'var(--color-info-bg)', border: '1px solid rgba(96,165,250,0.2)' }}
            >
              <Network size={16} color="var(--color-info)" strokeWidth={2} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <h1 className="page-title">Knowledge Graph</h1>
                {isDemo && (
                  <span
                    style={{
                      fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px',
                      background: 'var(--color-warning-bg)', color: 'var(--color-warning)',
                      border: '1px solid rgba(245,158,11,0.25)', padding: '3px 8px', borderRadius: 4,
                    }}
                  >
                    Demo Mode
                  </span>
                )}
              </div>
              <p className="page-subtitle">
                Error → Concept → Fix → Practice Problem graph
              </p>
            </div>
          </div>

          <button className="btn btn-secondary btn-sm" onClick={load} disabled={loading}>
            <RefreshCw size={13} style={{ animation: loading ? 'spin 0.8s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>

        {isDemo && (
          <div
            style={{
              display: 'flex', alignItems: 'center', gap: 8,
              marginTop: 14, padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--color-warning-bg)',
              border: '1px solid rgba(245,158,11,0.2)',
              fontSize: 12.5, color: 'var(--color-warning)',
            }}
          >
            <AlertCircle size={13} />
            Neo4j not connected — showing demo graph data. Start Neo4j Desktop and run{' '}
            <code style={{ fontFamily: 'JetBrains Mono', background: 'rgba(0,0,0,0.3)', padding: '1px 6px', borderRadius: 4 }}>
              python -m graph.ingest_graph
            </code>
          </div>
        )}
      </div>

      <div className="page-body">
        {/* Stats */}
        {statItems.length > 0 && (
          <div className="stats-grid animate-fade-in">
            {statItems.map(([key, value]) => (
              <div key={key} className="stat-card">
                <div className="stat-number" style={{ color: STAT_COLORS[key] || 'var(--accent-primary)' }}>
                  {value ?? '—'}
                </div>
                <div className="stat-label">{key}</div>
              </div>
            ))}
          </div>
        )}

        {/* Graph Search */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              className="form-input"
              type="text"
              placeholder="Search graph for an error (e.g. NullPointerException)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              disabled={isDemo || searching}
              style={{ paddingLeft: 34 }}
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-sm"
            disabled={isDemo || searching || !searchQuery.trim()}
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Search Results */}
        {searchResults && searchResults.results && (
          <div style={{ marginBottom: 16, padding: '12px 16px', borderRadius: 'var(--radius-sm)', background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
              Found {searchResults.count} result{searchResults.count !== 1 ? 's' : ''} for "{searchResults.query}"
            </div>
            {searchResults.results.slice(0, 5).map((item, i) => (
              <div key={i} style={{ padding: '8px 0', borderTop: i > 0 ? '1px solid var(--border-subtle)' : 'none', fontSize: 13, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                {item.error && <span style={{ color: 'var(--color-error)' }}>Error: <strong>{item.error.name}</strong></span>}
                {item.concept && <span style={{ color: 'var(--color-info)' }}>Concept: {item.concept.name}</span>}
                {item.fix && <span style={{ color: 'var(--color-success)' }}>Fix: {item.fix.description}</span>}
              </div>
            ))}
          </div>
        )}

        {/* Graph */}
        {loading ? (
          <div style={{ height: 520, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="loading-ring" />
          </div>
        ) : (
          <div className="animate-fade-in">
            <GraphVisualization data={graphData} height={520} />
            <div style={{ marginTop: 10, fontSize: 12, color: 'var(--text-muted)', textAlign: 'center' }}>
              Click a node to inspect · Scroll to zoom · Drag to pan
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
