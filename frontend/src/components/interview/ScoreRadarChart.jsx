import React from 'react';

export const ScoreRadarChart = ({ data = {} }) => {
  const entries = Object.entries(data);
  if (entries.length === 0) {
    return (
      <div className="text-center py-6 text-slate-500 text-xs">
        No competency breakdown available
      </div>
    );
  }

  // Draw SVG Radar Polygon
  const size = 260;
  const center = size / 2;
  const radius = 90;
  const total = entries.length;

  const getCoordinates = (index, value) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    const distance = (value / 100) * radius;
    const x = center + distance * Math.cos(angle);
    const y = center + distance * Math.sin(angle);
    return { x, y };
  };

  // Polygon points
  const points = entries.map(([_, val], i) => {
    const { x, y } = getCoordinates(i, val);
    return `${x},${y}`;
  }).join(' ');

  // Background Web concentric circles
  const levels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="overflow-visible">
        {/* Background webs */}
        {levels.map((lvl, lIdx) => (
          <polygon
            key={lIdx}
            points={entries.map((_, i) => {
              const { x, y } = getCoordinates(i, lvl * 100);
              return `${x},${y}`;
            }).join(' ')}
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="1"
          />
        ))}

        {/* Axis spokes */}
        {entries.map(([label], i) => {
          const { x, y } = getCoordinates(i, 100);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              stroke="rgba(255, 255, 255, 0.12)"
              strokeWidth="1"
            />
          );
        })}

        {/* Filled Data Polygon */}
        <polygon
          points={points}
          fill="rgba(59, 130, 246, 0.3)"
          stroke="#3b82f6"
          strokeWidth="2.5"
          className="transition-all duration-700"
        />

        {/* Vertex Points */}
        {entries.map(([label, val], i) => {
          const { x, y } = getCoordinates(i, val);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="4"
              fill="#60a5fa"
              stroke="#1e3a8a"
              strokeWidth="1.5"
            />
          );
        })}
      </svg>

      {/* Competency Horizontal Progress Bars */}
      <div className="w-full space-y-3 mt-4">
        {entries.map(([label, score], idx) => (
          <div key={idx} className="space-y-1">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-slate-300">{label}</span>
              <span className="text-brand-400 font-semibold">{score}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full transition-all duration-700"
                style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
