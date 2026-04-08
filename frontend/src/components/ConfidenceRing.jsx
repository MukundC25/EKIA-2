export default function ConfidenceRing({ score }) {
  const pct = Math.round((score || 0) * 100);
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - (score || 0));

  const color =
    pct >= 80 ? 'var(--color-success)' :
    pct >= 55 ? 'var(--color-warning)' :
                'var(--color-error)';

  const label = pct >= 80 ? 'High' : pct >= 55 ? 'Medium' : 'Low';

  return (
    <div className="confidence-wrapper">
      <div className="confidence-meta">
        <div className="confidence-label">Confidence</div>
        <div className="confidence-value" style={{ color }}>{label} · {pct}%</div>
      </div>

      <div style={{ position: 'relative', width: 50, height: 50, flexShrink: 0 }}>
        <svg width={50} height={50} style={{ transform: 'rotate(-90deg)' }}>
          <circle
            cx={25} cy={25} r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={3.5}
          />
          <circle
            cx={25} cy={25} r={radius}
            fill="none"
            stroke={color}
            strokeWidth={3.5}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: 'stroke-dashoffset 0.8s ease', filter: `drop-shadow(0 0 3px ${color})` }}
          />
        </svg>
        <div
          style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 10, fontWeight: 700, color,
          }}
        >
          {pct}%
        </div>
      </div>
    </div>
  );
}
