import clsx from 'clsx';

const sizes = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-10 h-10 border-[3px]',
  xl: 'w-16 h-16 border-4',
};

function LoadingSpinner({ size = 'md', className = '', label = 'Loading…' }) {
  return (
    <div role="status" aria-label={label} className={clsx('flex items-center justify-center', className)}>
      <div className={clsx('rounded-full border-slate-200 border-t-primary-600 animate-spin', sizes[size])} />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export default LoadingSpinner;
