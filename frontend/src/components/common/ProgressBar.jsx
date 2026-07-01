import clsx from 'clsx';

function ProgressBar({ value = 0, max = 100, label, showValue = true, size = 'md', colorClass }) {
  const pct = Math.min(Math.round((value / max) * 100), 100);
  const color = colorClass || _autoColor(pct);

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1.5">
          {label && <span className="text-sm font-medium text-slate-700">{label}</span>}
          {showValue && <span className="text-sm font-semibold text-slate-600 tabular-nums">{pct}%</span>}
        </div>
      )}
      <div className={clsx('w-full bg-slate-100 rounded-full overflow-hidden', {
        'h-1.5': size === 'sm',
        'h-2.5': size === 'md',
        'h-4':   size === 'lg',
      })}>
        <div
          className={clsx('h-full rounded-full transition-all duration-700', color)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function _autoColor(pct) {
  if (pct >= 80) return 'bg-success-500';
  if (pct >= 60) return 'bg-primary-500';
  if (pct >= 40) return 'bg-warning-500';
  return 'bg-danger-500';
}

export default ProgressBar;
