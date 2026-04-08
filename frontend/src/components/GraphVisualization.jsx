import { useCallback, useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

// Color map for node types — warm, non-purple palette
const NODE_COLORS = {
  Error:    '#ef4444',
  Concept:  '#60a5fa',
  Fix:      '#22c55e',
  Problem:  '#e8640c',
  Language: '#f59e0b',
  Unknown:  '#6b7280',
};

const NODE_SIZES = {
  Error: 7,
  Concept: 6,
  Fix: 5,
  Problem: 5,
  Language: 8,
  Unknown: 5,
};

const LEGEND_ITEMS = Object.entries(NODE_COLORS).filter(([k]) => k !== 'Unknown');

export default function GraphVisualization({ data, height = 500 }) {
  const containerRef = useRef(null);
  const graphRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [width, setWidth] = useState(800);

  useEffect(() => {
    if (containerRef.current) {
      setWidth(containerRef.current.offsetWidth);
    }
    const ro = new ResizeObserver(([entry]) => {
      setWidth(entry.contentRect.width);
    });
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 500);
      graphRef.current.zoom(3, 500);
    }
  }, []);

  const handleBackgroundClick = () => setSelectedNode(null);

  if (!data || !data.nodes?.length) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
          flexDirection: 'column',
          gap: 12,
          background: 'var(--bg-surface)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <div style={{ fontSize: 32 }}>🔗</div>
        <div style={{ fontSize: 14 }}>No graph data available</div>
        <div style={{ fontSize: 12 }}>Connect Neo4j and run the ingestion script</div>
      </div>
    );
  }

  const graphData = {
    nodes: data.nodes.map((n) => ({
      ...n,
      color: NODE_COLORS[n.type] || NODE_COLORS.Unknown,
      size: NODE_SIZES[n.type] || 5,
    })),
    links: data.edges.map((e) => ({
      source: e.source,
      target: e.target,
      label: e.relationship,
    })),
  };

  return (
    <div className="graph-container" style={{ height }} ref={containerRef}>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={width}
        height={height}
        backgroundColor="#0a0a0a"
        nodeColor={(n) => n.color}
        nodeRelSize={4}
        nodeVal={(n) => n.size}
        nodeLabel={(n) => `${n.type}: ${n.label}`}
        linkColor={() => 'rgba(255,255,255,0.12)'}
        linkWidth={1}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={1}
        linkDirectionalParticleColor={() => 'rgba(232,100,12,0.5)'}
        onNodeClick={handleNodeClick}
        onBackgroundClick={handleBackgroundClick}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const size = (node.size || 5) * 2;
          const isSelected = selectedNode?.id === node.id;

          // Glow for selected
          if (isSelected) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
            const grd = ctx.createRadialGradient(node.x, node.y, size, node.x, node.y, size + 8);
            grd.addColorStop(0, node.color + '60');
            grd.addColorStop(1, 'transparent');
            ctx.fillStyle = grd;
            ctx.fill();
          }

          // Main dot
          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = node.color;
          ctx.fill();

          // Border
          ctx.strokeStyle = isSelected ? 'white' : 'rgba(255,255,255,0.15)';
          ctx.lineWidth = isSelected ? 1.5 : 0.5;
          ctx.stroke();

          // Label at medium zoom
          if (globalScale >= 1.5 || isSelected) {
            const label = node.label?.slice(0, 20) || '';
            ctx.font = `${Math.max(8, 10 / globalScale)}px Inter, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            // Background for readability
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = 'rgba(5, 11, 24, 0.75)';
            ctx.fillRect(node.x - textWidth / 2 - 2, node.y + size + 2, textWidth + 4, 12 / globalScale);
            ctx.fillStyle = node.color;
            ctx.fillText(label, node.x, node.y + size + 8 / globalScale);
          }
        }}
        cooldownTicks={80}
        onEngineStop={() => graphRef.current?.zoomToFit(300, 40)}
      />

      {/* Legend */}
      <div className="graph-legend">
        {LEGEND_ITEMS.map(([type, color]) => (
          <div key={type} className="legend-item">
            <div className="legend-dot" style={{ background: color }} />
            <span>{type}</span>
          </div>
        ))}
      </div>

      {/* Selected Node Info Panel */}
      {selectedNode && (
        <div className="graph-node-info glass-card-elevated" style={{ padding: 16, fontSize: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
            <span
              style={{
                fontSize: 10,
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: 1,
                color: NODE_COLORS[selectedNode.type] || 'var(--text-muted)',
              }}
            >
              {selectedNode.type}
            </span>
            <button
              onClick={() => setSelectedNode(null)}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 16 }}
            >
              ×
            </button>
          </div>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
            {selectedNode.label}
          </div>
          {selectedNode.properties &&
            Object.entries(selectedNode.properties)
              .filter(([k, v]) => v && k !== 'name' && k !== 'id')
              .slice(0, 4)
              .map(([k, v]) => (
                <div key={k} style={{ marginBottom: 4, color: 'var(--text-secondary)' }}>
                  <span style={{ color: 'var(--text-muted)', fontFamily: 'JetBrains Mono', fontSize: 11 }}>{k}: </span>
                  {String(v).slice(0, 60)}
                </div>
              ))}
        </div>
      )}
    </div>
  );
}
