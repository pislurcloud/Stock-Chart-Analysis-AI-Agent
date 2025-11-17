interface MetricsCardProps {
  label: string
  value: string | number
  className?: string
}

export function MetricsCard({ label, value, className = '' }: MetricsCardProps) {
  return (
    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
      <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">
        {label}
      </div>
      <div className={`text-lg font-semibold ${className || 'text-slate-900 dark:text-white'}`}>
        {value}
      </div>
    </div>
  )
}
