'use client'

import { useState } from 'react'
import { Search, TrendingUp } from 'lucide-react'

interface AnalysisFormProps {
  onAnalyze: (symbol: string, timeframe: string) => void
  loading: boolean
}

const NIFTY50_STOCKS = [
  'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
  'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
  'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA',
  'TITAN', 'ULTRACEMCO', 'BAJFINANCE', 'NESTLEIND', 'WIPRO',
  'HCLTECH', 'TATAMOTORS', 'ONGC', 'NTPC', 'POWERGRID',
  'ADANIPORTS', 'COALINDIA', 'TATASTEEL', 'M&M', 'JSWSTEEL'
]

const TIMEFRAMES = [
  { value: '15m', label: '15 Minutes' },
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1wk', label: '1 Week' },
]

export function AnalysisForm({ onAnalyze, loading }: AnalysisFormProps) {
  const [symbol, setSymbol] = useState('')
  const [timeframe, setTimeframe] = useState('1d')
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (symbol.trim()) {
      onAnalyze(symbol.toUpperCase().trim(), timeframe)
      setShowSuggestions(false)
    }
  }

  const filteredSuggestions = NIFTY50_STOCKS.filter(stock =>
    stock.toLowerCase().includes(symbol.toLowerCase())
  ).slice(0, 10)

  const selectSuggestion = (stock: string) => {
    setSymbol(stock)
    setShowSuggestions(false)
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700">
      <form onSubmit={handleSubmit}>
        <div className="grid md:grid-cols-[1fr_auto_auto] gap-4">
          {/* Symbol Input */}
          <div className="relative">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Stock Symbol
            </label>
            <div className="relative">
              <input
                type="text"
                value={symbol}
                onChange={(e) => {
                  setSymbol(e.target.value)
                  setShowSuggestions(true)
                }}
                onFocus={() => setShowSuggestions(true)}
                placeholder="e.g., RELIANCE, TCS, INFY"
                className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                disabled={loading}
              />
              <Search className="absolute right-3 top-3.5 h-5 w-5 text-slate-400" />
            </div>

            {/* Suggestions Dropdown */}
            {showSuggestions && symbol && filteredSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg shadow-lg max-h-60 overflow-auto">
                {filteredSuggestions.map((stock) => (
                  <button
                    key={stock}
                    type="button"
                    onClick={() => selectSuggestion(stock)}
                    className="w-full px-4 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-600 text-slate-900 dark:text-white transition-colors flex items-center space-x-2"
                  >
                    <TrendingUp className="h-4 w-4 text-primary" />
                    <span>{stock}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Timeframe Select */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full md:w-auto px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              disabled={loading}
            >
              {TIMEFRAMES.map((tf) => (
                <option key={tf.value} value={tf.value}>
                  {tf.label}
                </option>
              ))}
            </select>
          </div>

          {/* Submit Button */}
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading || !symbol.trim()}
              className="w-full md:w-auto px-8 py-3 bg-primary hover:bg-primary/90 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-sm text-slate-600 dark:text-slate-400">
            Quick select:
          </span>
          {['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'TATAMOTORS'].map((stock) => (
            <button
              key={stock}
              type="button"
              onClick={() => setSymbol(stock)}
              className="px-3 py-1 text-sm bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded-full transition-colors"
              disabled={loading}
            >
              {stock}
            </button>
          ))}
        </div>
      </form>
    </div>
  )
}
