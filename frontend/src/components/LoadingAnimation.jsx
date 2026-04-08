import { useEffect, useState } from 'react';
import { Search, Database, Network, Brain, ShieldCheck, CheckCircle2 } from 'lucide-react';

const STEPS = [
  { icon: Search,       label: 'Parsing error query...' },
  { icon: Database,     label: 'Searching vector knowledge base...' },
  { icon: Network,      label: 'Querying knowledge graph...' },
  { icon: Brain,        label: 'Llama3 reasoning over context...' },
  { icon: ShieldCheck,  label: 'Validating response structure...' },
  { icon: CheckCircle2, label: 'Preparing final analysis...' },
];

export default function LoadingAnimation() {
  const [activeStep, setActiveStep] = useState(0);
  const [doneSteps, setDoneSteps] = useState(new Set());

  useEffect(() => {
    const timers = [];
    const delays = [0, 1200, 2800, 4400, 7000, 9000];
    delays.forEach((delay, i) => {
      timers.push(setTimeout(() => setActiveStep(i), delay));
      if (i > 0) {
        timers.push(setTimeout(() => setDoneSteps((prev) => new Set([...prev, i - 1])), delay + 600));
      }
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="glass-card-elevated loading-container animate-fade-in">
      <div className="loading-ring" />

      <div>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>
            Running EKIA Agent Pipeline
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
            5-node LangGraph · Llama3 · FAISS · Neo4j
          </div>
        </div>

        <div className="loading-steps">
          {STEPS.map((step, i) => {
            const isDone   = doneSteps.has(i);
            const isActive = activeStep === i && !isDone;
            const StepIcon = isDone ? CheckCircle2 : step.icon;

            return (
              <div
                key={i}
                className={`loading-step ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
              >
                <StepIcon
                  size={13}
                  style={{
                    flexShrink: 0,
                    color: isDone
                      ? 'var(--color-success)'
                      : isActive
                      ? 'var(--accent-primary)'
                      : 'var(--text-muted)',
                  }}
                />
                <span>{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ fontSize: 11.5, color: 'var(--text-muted)', textAlign: 'center', lineHeight: 1.7 }}>
        First run may take 20–60 s while models load
      </div>
    </div>
  );
}
