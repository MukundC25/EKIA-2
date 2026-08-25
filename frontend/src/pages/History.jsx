import { History as HistoryIcon, Clock, ExternalLink, BarChart3, Bug } from 'lucide-react';

import { useState, useEffect } from 'react';
import { getDebugHistory } from '../services/api';

function ConfidenceBadge({ score }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? 'var(--color-success)' :
    pct >= 55 ? 'var(--color-warning)' :
                'var(--color-error)';
  return (
    <span
      style={{
        fontSize: 11, fontWeight: 700, fontFamily: 'JetBrains Mono',
        color,
        background: `${color}14`,
        border: `1px solid ${color}33`,
        padding: '3px 8px', borderRadius: 5,
      }}
    >
      {pct}%
    </span>
  );
}

const LANG_COLORS = {
  Java: 'var(--color-error)',
  Python: 'var(--color-info)',
  React: 'var(--text-accent)',
  JavaScript: 'var(--color-warning)',
};

export default function History() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const langfuseUrl = import.meta.env.VITE_LANGFUSE_HOST || 'https://cloud.langfuse.com';

  useEffect(() => {
    getDebugHistory()
      .then((data) => {
        setSessions(data.sessions || []);
      })
      .catch((err) => console.error("Failed to load history", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="main-content">
      <div className="page-header">
        <div className="page-header-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              className="page-icon-box"
              style={{ background: 'rgba(160,160,160,0.08)', border: '1px solid var(--border-default)' }}
            >
              <HistoryIcon size={16} color="var(--text-secondary)" strokeWidth={2} />
            </div>
            <div>
              <h1 className="page-title">Debug History</h1>
              <p className="page-subtitle">
                Recent sessions · Full traces available in Langfuse
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="page-body">
        {/* Langfuse Banner */}
        <div className="info-banner animate-fade-in" style={{ marginBottom: 20 }}>
          <BarChart3 size={18} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: 1 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, marginBottom: 3 }}>Full Observability in Langfuse</div>
            <div style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
              Every debug session is traced with confidence scores, input/output, and latency metrics.
            </div>
          </div>
          <a
            href={langfuseUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary btn-sm"
            style={{ flexShrink: 0 }}
          >
            <ExternalLink size={13} />
            Open Dashboard
          </a>
        </div>

        {/* Session list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>Loading history...</div>
          ) : sessions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>No debug sessions yet.</div>
          ) : (
            sessions.map((session, i) => (
              <div
                key={session.id}
                className="history-card animate-fade-in-up"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div
                    style={{
                      width: 34, height: 34, borderRadius: 7,
                      background: 'var(--color-error-bg)',
                      border: '1px solid var(--color-error-border)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <Bug size={14} color="var(--color-error)" />
                  </div>
                  <div>
                    <div
                      style={{
                        fontFamily: 'JetBrains Mono',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        fontSize: 13.5,
                        marginBottom: 3,
                      }}
                    >
                      {session.error}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: 'var(--text-muted)' }}>
                      <span
                        style={{
                          fontSize: 10.5, fontWeight: 600,
                          color: LANG_COLORS[session.language] || 'var(--text-secondary)',
                          background: 'rgba(255,255,255,0.05)',
                          border: `1px solid rgba(255,255,255,0.08)`,
                          padding: '2px 7px', borderRadius: 4,
                        }}
                      >
                        {session.language}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <Clock size={11} />
                        {session.timestamp}
                      </span>
                      {session.trace_id && (
                        <span style={{ fontFamily: 'JetBrains Mono', fontSize: 10.5, color: 'var(--text-muted)' }}>
                          {session.trace_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <ConfidenceBadge score={session.confidence} />
              </div>
            ))
          )}
        </div>

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: 'var(--text-muted)' }}>
          Powered by local SQLite persistence.
        </div>
      </div>
    </div>
  );
}
