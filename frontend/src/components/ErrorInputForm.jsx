import { useState } from 'react';
import { Send, RotateCcw, Code2, MessageSquare, Zap } from 'lucide-react';

const LANGUAGES = [
  { value: 'other',      label: 'Auto-detect' },
  { value: 'java',       label: 'Java' },
  { value: 'python',     label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'react',      label: 'React' },
  { value: 'c++',        label: 'C++' },
  { value: 'c',          label: 'C' },
  { value: 'sql',        label: 'SQL' },
  { value: 'docker',     label: 'Docker / K8s' },
  { value: 'go',         label: 'Go' },
  { value: 'rust',       label: 'Rust' },
];

const QUICK_EXAMPLES = [
  { label: 'Java NPE',       error: 'NullPointerException', language: 'java',       context: 'Calling user.getName() but user can be null from a database query' },
  { label: 'Python KeyError', error: "KeyError: 'user_id'", language: 'python',    context: 'Accessing a dictionary key that might not exist' },
  { label: 'React Loop',     error: 'Maximum update depth exceeded', language: 'react', context: 'Inside useEffect that updates state without proper dependency array' },
  { label: 'JS TypeError',   error: "TypeError: Cannot read properties of undefined (reading 'map')", language: 'javascript', context: 'API response not yet loaded when component renders' },
];

export default function ErrorInputForm({ onSubmit, isLoading }) {
  const [form, setForm] = useState({ error: '', language: 'other', context: '', code_snippet: '' });
  const [showCode, setShowCode] = useState(false);

  const set = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.error.trim()) return;
    onSubmit(form);
  };

  const handleReset = () => {
    setForm({ error: '', language: 'other', context: '', code_snippet: '' });
    setShowCode(false);
  };

  return (
    <div className="glass-card-elevated" style={{ padding: '22px 24px' }}>
      {/* Quick Examples */}
      <div style={{ marginBottom: 20 }}>
        <div className="form-label">
          <Zap size={11} />
          Quick Examples
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {QUICK_EXAMPLES.map((ex) => (
            <button
              key={ex.label}
              className="btn btn-ghost btn-sm"
              onClick={() => set('error', ex.error) || setForm((p) => ({ ...p, error: ex.error, language: ex.language, context: ex.context }))}
              type="button"
              disabled={isLoading}
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Error Input */}
        <div className="form-group">
          <label className="form-label">
            <Code2 size={11} />
            Error Message / Stack Trace
            <span style={{ color: 'var(--color-error)', marginLeft: 2 }}>*</span>
          </label>
          <textarea
            id="error-input"
            className="form-textarea error-input"
            placeholder={`NullPointerException at UserService.java:42\n  or\nKeyError: 'user_id'`}
            value={form.error}
            onChange={(e) => set('error', e.target.value)}
            rows={5}
            disabled={isLoading}
            required
          />
        </div>

        {/* Language + Context */}
        <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr', gap: 14, marginBottom: 18 }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Language</label>
            <select
              id="language-select"
              className="form-select"
              value={form.language}
              onChange={(e) => set('language', e.target.value)}
              disabled={isLoading}
            >
              {LANGUAGES.map((l) => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">
              <MessageSquare size={11} />
              Context
              <span style={{ fontWeight: 400, textTransform: 'none', fontSize: 11, letterSpacing: 0, color: 'var(--text-muted)'  }}>(optional)</span>
            </label>
            <input
              id="context-input"
              className="form-input"
              type="text"
              placeholder="What were you doing when this happened?"
              value={form.context}
              onChange={(e) => set('context', e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Code Snippet */}
        <div style={{ marginBottom: 18 }}>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => setShowCode((v) => !v)}
            disabled={isLoading}
          >
            <Code2 size={13} />
            {showCode ? 'Hide' : 'Add'} Code Snippet
          </button>

          {showCode && (
            <div className="form-group" style={{ marginTop: 10, marginBottom: 0 }}>
              <textarea
                id="code-snippet-input"
                className="form-textarea"
                placeholder="// Paste the relevant code where the error occurs..."
                value={form.code_snippet}
                onChange={(e) => set('code_snippet', e.target.value)}
                rows={6}
                disabled={isLoading}
              />
            </div>
          )}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            id="analyze-btn"
            type="submit"
            className="btn btn-primary btn-lg btn-full"
            style={{ flex: 1 }}
            disabled={isLoading || !form.error.trim()}
          >
            {isLoading ? (
              <><div className="btn-spinner" />Analyzing...</>
            ) : (
              <><Send size={15} />Analyze Error</>
            )}
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleReset}
            disabled={isLoading}
            title="Clear form"
          >
            <RotateCcw size={15} />
          </button>
        </div>
      </form>
    </div>
  );
}
