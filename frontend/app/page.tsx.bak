'use client'

import { useState } from 'react'
import { AnalysisForm } from '@/components/AnalysisForm'
import { AnalysisResults } from '@/components/AnalysisResults'
import { Header } from '@/components/Header'
import { Loader2 } from 'lucide-react'

export default function Home() {
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async (symbol: string, timeframe: string) => {
    setLoading(true)
    setError(null)
    setAnalysisData(null)

    try {
      const response = await fetch('/api/analyze-ai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol, timeframe }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const data = await response.json()
      setAnalysisData(data)
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white mb-4">
            Stock Analysis AI
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            AI-powered technical analysis for Indian NSE stocks with pattern recognition,
            scenario playbook, and professional downloadable reports
          </p>
        </div>

        {/* Analysis Form */}
        <div className="mb-8">
          <AnalysisForm onAnalyze={handleAnalyze} loading={loading} />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-lg text-slate-600 dark:text-slate-300">
              Running AI analysis...
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              This may take 30-60 seconds
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
            <p className="text-red-800 dark:text-red-200 font-semibold mb-2">
              Analysis Failed
            </p>
            <p className="text-red-600 dark:text-red-300">
              {error}
            </p>
          </div>
        )}

        {/* Results */}
        {!loading && !error && analysisData && (
          <AnalysisResults data={analysisData} />
        )}

        {/* Empty State */}
        {!loading && !error && !analysisData && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <svg
                className="w-8 h-8 text-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              Ready to Analyze
            </h3>
            <p className="text-slate-600 dark:text-slate-300">
              Enter a stock symbol above to get started with AI-powered analysis
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-700 mt-16 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Stock Analysis AI © 2025 | For educational purposes only | Not financial advice
          </p>
        </div>
      </footer>
    </div>
  )
}
