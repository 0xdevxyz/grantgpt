export default function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-4',
  };

  return (
    <div
      className={`inline-block animate-spin rounded-full border-blue-600 border-t-transparent ${sizeClasses[size]}`}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Laden...</span>
    </div>
  );
}
