import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
};

const variantClasses = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  white: 'text-white',
};

export default function LoadingSpinner({ 
  size = 'md', 
  variant = 'primary',
  className = '' 
}: LoadingSpinnerProps) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <svg
        className={`animate-spin ${sizeClasses[size]} ${variantClasses[variant]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}

// Also export as named export for flexibility
export { LoadingSpinner };

// Full screen loading spinner
export function FullScreenSpinner() {
  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-900 flex items-center justify-center z-50">
      <div className="text-center">
        <LoadingSpinner size="xl" variant="primary" />
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
          Loading...
        </p>
      </div>
    </div>
  );
}

// Page loading spinner
export function PageSpinner() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="xl" variant="primary" />
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
          Loading page...
        </p>
      </div>
    </div>
  );
}

// Inline loading spinner
export function InlineSpinner({ size = 'sm', className = '' }: Omit<LoadingSpinnerProps, 'variant'>) {
  return <LoadingSpinner size={size} variant="secondary" className={className} />;
}
