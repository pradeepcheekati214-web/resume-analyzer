import { HiOutlineChartBar } from 'react-icons/hi';

const COLORS = ['bg-primary-500', 'bg-secondary-500', 'bg-success-500', 'bg-warning-500', 'bg-purple-500'];

function ScoreBreakdown({ breakdown }) {
  if (!breakdown || typeof breakdown !== 'object' || Object.keys(breakdown).length === 0) return null;

  const entries = Object.entries(breakdown).map(([key, val], i) => ({
    label: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    score: typeof val === 'object' ? val.score ?? 0 : val,
    max:   typeof val === 'object' ? val.max   ?? 100 : 100,
    color: COLORS[i % COLORS.length],
  }));

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-5">
        <HiOutlineChartBar className="w-5 h-5 text-primary-600" />
        <h2 className="font-semibold text-slate-900">Score Breakdown</h2>
      </div>

      <div className="space-y-4">
        {entries.map(({ label, score, max, color }) => {
          const pct = Math.min(Math.round((score / max) * 100), 100);
          return (
            <div key={label}>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="font-medium text-slate-700">{label}</span>
                <span className="text-slate-500 tabular-nums">{score}<span className="text-slate-300">/{max}</span></span>
              </div>
              <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                <div
                  className={`h-full rounded-full ${color} transition-all duration-700`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ScoreBreakdown;
