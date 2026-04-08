import { useState } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import js      from 'react-syntax-highlighter/dist/esm/languages/hljs/javascript';
import java    from 'react-syntax-highlighter/dist/esm/languages/hljs/java';
import python  from 'react-syntax-highlighter/dist/esm/languages/hljs/python';
import cpp     from 'react-syntax-highlighter/dist/esm/languages/hljs/cpp';
import sql     from 'react-syntax-highlighter/dist/esm/languages/hljs/sql';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import {
  Copy, Check, ChevronDown, ChevronUp, ExternalLink,
  Target, Users, Wrench, BookOpen, Link2, AlertTriangle,
} from 'lucide-react';
import ConfidenceRing from './ConfidenceRing';
import ConceptTags from './ConceptTags';

SyntaxHighlighter.registerLanguage('javascript', js);
SyntaxHighlighter.registerLanguage('java', java);
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('cpp', cpp);
SyntaxHighlighter.registerLanguage('sql', sql);

// ---------------------------------------------------------------------------
// Code block with copy button
// ---------------------------------------------------------------------------
function CodeBlock({ code, language = 'javascript' }) {
  const [copied, setCopied] = useState(false);
  const lang = language === 'c++' ? 'cpp' : language === 'react' ? 'javascript' : language;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <div className="code-block-wrapper">
      <button
        onClick={handleCopy}
        className={`code-copy-btn ${copied ? 'copied' : ''}`}
      >
        {copied ? <Check size={11} /> : <Copy size={11} />}
        {copied ? 'Copied' : 'Copy'}
      </button>
      <SyntaxHighlighter
        language={lang}
        style={atomOneDark}
        customStyle={{
          margin: 0,
          padding: '14px 16px',
          fontSize: 12.5,
          background: 'rgba(5, 5, 5, 0.85)',
          borderRadius: 0,
          lineHeight: 1.65,
        }}
        showLineNumbers
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Collapsible section
// ---------------------------------------------------------------------------
function Section({ icon: Icon, title, variant, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`result-section ${variant ? `variant-${variant}` : ''}`}>
      <div
        className={`result-section-header ${open ? 'open' : ''}`}
        onClick={() => setOpen((v) => !v)}
      >
        <div className="result-section-title">
          {Icon && <Icon size={12} strokeWidth={2.5} />}
          {title}
        </div>
        {open ? <ChevronUp size={13} style={{ color: 'var(--text-muted)' }} />
               : <ChevronDown size={13} style={{ color: 'var(--text-muted)' }} />}
      </div>
      {open && (
        <div className="result-section-body">
          {children}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main result card
// ---------------------------------------------------------------------------
export default function DebugResultCard({ result }) {
  if (!result) return null;

  const lang = result.graph_context?.[0]?.error?.language?.toLowerCase() || 'javascript';

  // Extract code lines from fix field (lines after the first paragraph)
  const fixLines = (result.fix || '').split('\n');
  const fixText  = fixLines[0];
  const fixCode  = fixLines.slice(1).join('\n').trim();

  return (
    <div className="result-card animate-fade-in-up">
      {/* Header */}
      <div className="result-header">
        <div style={{ flex: 1 }}>
          <div className="result-error-tag">
            <AlertTriangle size={10} strokeWidth={2.5} />
            Error Analysis
          </div>
          <div className="result-error-name">{result.error}</div>
          {result.trace_id && (
            <div
              style={{
                display: 'flex', alignItems: 'center', gap: 5,
                marginTop: 8, fontSize: 11, color: 'var(--text-muted)',
                fontFamily: 'JetBrains Mono',
              }}
            >
              <ExternalLink size={10} />
              Trace: {result.trace_id}
            </div>
          )}
        </div>
        <ConfidenceRing score={result.confidence_score} />
      </div>

      {/* Body */}
      <div className="result-body">
        {/* Root Cause */}
        <Section icon={Target} title="Root Cause" variant="error">
          <p className="result-section-text">{result.root_cause}</p>
        </Section>

        {/* Explanations side by side */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <Section icon={Users} title="Simple Explanation" defaultOpen={true}>
            <p className="result-section-text" style={{ fontSize: 13 }}>
              {result.beginner_explanation}
            </p>
          </Section>
          <Section icon={Wrench} title="Technical Analysis" defaultOpen={true}>
            <p className="result-section-text" style={{ fontSize: 13 }}>
              {result.technical_explanation}
            </p>
          </Section>
        </div>

        {/* Fix */}
        <Section icon={Check} title="Recommended Fix" variant="success">
          {fixText && (
            <p className="result-section-text" style={{ marginBottom: fixCode ? 10 : 0 }}>
              {fixText}
            </p>
          )}
          {fixCode && <CodeBlock code={fixCode} language={lang} />}
          {!fixCode && result.fix && <CodeBlock code={result.fix} language={lang} />}
        </Section>

        {/* Learning resources */}
        <Section icon={BookOpen} title="Learning Resources" variant="info">
          <ConceptTags
            concepts={result.related_concepts}
            problems={result.practice_problems}
            sources={result.sources}
          />
        </Section>

        {/* Graph context */}
        {result.graph_context && result.graph_context.length > 0 && (
          <Section icon={Link2} title="Knowledge Graph Context">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {result.graph_context.slice(0, 3).map((item, i) => (
                <div
                  key={i}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 6,
                    background: 'var(--bg-hover)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: 12.5,
                    display: 'flex',
                    gap: 12,
                    flexWrap: 'wrap',
                  }}
                >
                  {item.concept && (
                    <span style={{ color: 'var(--color-info)' }}>
                      Concept: <strong>{item.concept.name}</strong>
                    </span>
                  )}
                  {item.fix && (
                    <span style={{ color: 'var(--color-success)' }}>
                      Fix: {item.fix.description}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}
