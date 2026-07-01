import { getScoreStrokeColor, getScoreColor, getScoreLabel } from '@/utils/constants';

/**
 * SVG circular progress ring showing the ATS score.
 * size — outer diameter in px (default 120)
 */
function ATSScoreRing({ score = 0, size = 120 }) {
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = getScoreStrokeColor(score);

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="#e2e8f0" strokeWidth={stroke}
        />
        {/* Progress */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-extrabold leading-none ${getScoreColor(score)}`}
              style={{ fontSize: size * 0.22 }}>
          {score}
        </span>
        <span className="text-slate-400 font-medium" style={{ fontSize: size * 0.09 }}>/ 100</span>
        <span className={`font-semibold mt-0.5 ${getScoreColor(score)}`}
              style={{ fontSize: size * 0.09 }}>
          {getScoreLabel(score)}
        </span>
      </div>
    </div>
  );
}

export default ATSScoreRing;
