import { useState } from 'react';
import ErrorInputForm from '../components/ErrorInputForm';
import DebugResultCard from '../components/DebugResultCard';
import LoadingAnimation from '../components/LoadingAnimation';
import { debugError } from '../services/api';
import { Bug, Cpu, Activity, Database, AlertCircle } from 'lucide-react';

const INFO_CHIPS = [
  { icon: Cpu,      label: 'LLM',        value: 'Llama3 · Ollama' },
  { icon: Activity, label: 'Embeddings', value: 'all-MiniLM-L6-v2' },
  { icon: Database, label: 'Vector DB',  value: 'FAISS (local)' },
  { icon: Bug,      label: 'Knowledge',  value: '25 errors' },
];

export default function Debugger() {
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await debugError(formData);
      setResult(response);
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'object' ? detail.message : detail || err.message;
      setError(msg || 'Analysis failed. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              className="page-icon-box"
              style={{ background: 'var(--color-error-bg)', border: '1px solid var(--color-error-border)' }}
            >
              <Bug size={16} color="var(--color-error)" strokeWidth={2} />
            </div>
            <div>
              <h1 className="page-title">AI Debugger</h1>
              <p className="page-subtitle">
                Paste any error — get root cause, fix, and learning resources
              </p>
            </div>
          </div>
        </div>

        {/* Info chips */}
        <div className="info-bar">
          {INFO_CHIPS.map(({ icon: Icon, label, value }) => (
            <div key={label} className="info-chip">
              <Icon size={12} />
              <span>{label}:</span>
              <span className="info-chip-value">{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="page-body">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 880 }}>
          {/* Input */}
          <ErrorInputForm onSubmit={handleSubmit} isLoading={loading} />

          {/* Error state */}
          {error && !loading && (
            <div className="error-banner animate-fade-in">
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                <AlertCircle size={16} color="var(--color-error)" style={{ flexShrink: 0, marginTop: 2 }} />
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 3 }}>
                    Analysis Failed
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{error}</div>
                </div>
              </div>
              <div className="error-hint">
                1. Backend running? &nbsp;<span style={{ color: 'var(--text-accent)' }}>uvicorn app.main:app --reload</span><br />
                2. Ollama running? &nbsp;&nbsp;<span style={{ color: 'var(--text-accent)' }}>ollama serve</span><br />
                3. Model pulled? &nbsp;&nbsp;&nbsp;&nbsp;<span style={{ color: 'var(--text-accent)' }}>ollama pull llama3</span>
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && <LoadingAnimation />}

          {/* Result */}
          {result && !loading && <DebugResultCard result={result} />}
        </div>
      </div>
    </div>
  );
}
