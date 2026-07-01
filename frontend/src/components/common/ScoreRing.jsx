import clsx from 'clsx';

/**
 * Reusable circular SVG progress ring.
 * Props: score (0-100), size (px), label, strokeWidth, color
 */
function ScoreRing({ score = 0, size = 120, label = '', strokeWidth = 10, color }) {
  const radius = (size - strokeWidth) / 2;
  const circ   = 2 * Math.PI * radius;
  const offset = circ - (Math.min(score, 100) / 100) * circ;

  const strokeColor = color || _autoColor(score);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={radius}
          fill="none" stroke="#e2e8f0" strokeWidth={strokeWidth} />
        <circle cx={size/2} cy={size/2} r={radius}
          fill="none" stroke={strokeColor} strokeWidth={strokeWidth}
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="font-extrabold leading-none" style={{ fontSize: size * 0.21, color: strokeColor }}>
          {Math.round(score)}
        </span>
        {label && (
          <span className="text-slate-400 font-medium text-center leading-tight mt-0.5"
            style={{ fontSize: size * 0.085 }}>
            {label}
          </span>
        )}
      </div>
    </div>
  );
}

function _autoColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#2563eb';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
}

export default ScoreRing;
