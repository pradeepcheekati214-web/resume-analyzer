import clsx from 'clsx';

const STYLES = {
  easy:   'bg-success-50 text-success-600 border border-success-200',
  medium: 'bg-warning-50 text-warning-600 border border-warning-200',
  hard:   'bg-danger-50  text-danger-600  border border-danger-200',
};

function DifficultyBadge({ difficulty = 'medium', className = '' }) {
  const level = difficulty.toLowerCase();
  return (
    <span className={clsx(
      'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold capitalize',
      STYLES[level] || STYLES.medium,
      className
    )}>
      {level}
    </span>
  );
}

export default DifficultyBadge;
