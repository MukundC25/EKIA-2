import { History as HistoryIcon, Clock, ExternalLink, BarChart3, Bug } from 'lucide-react';

const MOCK_SESSIONS = [
  { id: 1, error: 'NullPointerException',          language: 'Java',       confidence: 0.92, timestamp: '2 minutes ago',  trace_id: 'tr-abc123' },
  { id: 2, error: "KeyError: 'user_id'",           language: 'Python',     confidence: 0.87, timestamp: '15 minutes ago', trace_id: 'tr-def456' },
  { id: 3, error: 'Maximum update depth exceeded', language: 'React',      confidence: 0.78, timestamp: '1 hour ago',     trace_id: 'tr-ghi789' },
];

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
  const langfuseUrl = import.meta.env.VITE_LANGFUSE_HOST || 'https://cloud.langfuse.com';

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
          {MOCK_SESSIONS.map((session, i) => (
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
                    <span style={{ fontFamily: 'JetBrains Mono', fontSize: 10.5, color: 'var(--text-muted)' }}>
                      {session.trace_id}
                    </span>
                  </div>
                </div>
              </div>
              <ConfidenceBadge score={session.confidence} />
            </div>
          ))}
        </div>

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: 'var(--text-muted)' }}>
          Connect a database to persist real history. Showing demo data.
        </div>
      </div>
    </div>
  );
}
