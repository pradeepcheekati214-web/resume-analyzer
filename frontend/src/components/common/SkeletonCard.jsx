import clsx from 'clsx';

/** Animated skeleton placeholder for loading states */
function SkeletonCard({ lines = 3, className = '' }) {
  return (
    <div className={clsx('card space-y-3 animate-pulse', className)}>
      <div className="h-4 bg-slate-200 rounded w-1/3" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="h-3 bg-slate-200 rounded" style={{ width: `${85 - i * 10}%` }} />
        </div>
      ))}
    </div>
  );
}

export function SkeletonGrid({ count = 3, cols = 3 }) {
  return (
    <div className={clsx('grid gap-4', {
      'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': cols === 3,
      'grid-cols-1 sm:grid-cols-2': cols === 2,
      'grid-cols-1': cols === 1,
    })}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} lines={3} />
      ))}
    </div>
  );
}

export default SkeletonCard;
