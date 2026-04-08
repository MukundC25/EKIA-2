import { BookOpen, Brain, Dumbbell, Database } from 'lucide-react';

export default function ConceptTags({ concepts = [], problems = [], sources = [] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {concepts.length > 0 && (
        <div>
          <div className="result-section-title" style={{ marginBottom: 8 }}>
            <Brain size={12} />
            Related Concepts
          </div>
          <div className="tag-list">
            {concepts.map((c, i) => (
              <span key={i} className="tag tag-concept">{c}</span>
            ))}
          </div>
        </div>
      )}

      {problems.length > 0 && (
        <div>
          <div className="result-section-title" style={{ marginBottom: 8, marginTop: concepts.length ? 8 : 0 }}>
            <Dumbbell size={12} />
            Practice Problems
          </div>
          <div className="tag-list">
            {problems.map((p, i) => (
              <span key={i} className="tag tag-problem">{p}</span>
            ))}
          </div>
        </div>
      )}

      {sources.length > 0 && (
        <div>
          <div className="result-section-title" style={{ marginBottom: 8, marginTop: 8 }}>
            <Database size={12} />
            Knowledge Sources
          </div>
          <div className="tag-list">
            {sources.map((s, i) => (
              <span key={i} className="tag tag-source">{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
