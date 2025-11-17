import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number, currency: string = "INR"): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-IN').format(value)
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(2)}%`
}

export function getRecommendationColor(recommendation: string): string {
  if (recommendation.includes('BUY') || recommendation.includes('BULLISH')) {
    return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
  } else if (recommendation.includes('SELL') || recommendation.includes('BEARISH')) {
    return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
  } else if (recommendation.includes('WAIT') || recommendation.includes('NEUTRAL')) {
    return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
  }
  return 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
}