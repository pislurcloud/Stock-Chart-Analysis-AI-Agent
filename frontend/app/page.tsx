'use client'

import { useState } from 'react'
import { Header } from '@/components/Header'
import { Loader2, TrendingUp, TrendingDown, AlertCircle, Download, BarChart3, FileText, Target } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

// Get API URL from environment - call backend directly to avoid Vercel proxy timeout
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AnalysisData {
  status: string
  symbol: string
  timeframe: string
  execution_time: number
  stock_info: {
    company_name: string
    sector: string
    market_cap?: number
  }
  latest_candle: {
    close: number
    volume: number
    timestamp?: string
  }
  technical_analysis: {
    overall_bias: string
    strength_score: number
    trend?: string
    momentum?: string
    key_levels?: {
      resistance_1?: number
      resistance_2?: number
      support_1?: number
      support_2?: number
    }
  }
  pattern_analysis: {
    market_structure: string
    patterns: Array<{ pattern: string; confidence: string }>
    confidence: string
  }
  risk_analysis: {
    scenarios: Array<{
      scenario: string
      entry: number
      stop: number
      target: number
      rr_ratio: number
      confidence: string
      warreni_take?: string
    }>
    backtest?: {
      estimated_success_rate: number
      lookback_period: string
    }
    risk_metrics?: {
      average_rr_ratio: number
      volatility_level: string
      risk_grade: string
    }
    position_sizing?: {
      recommended_position: string
      rationale: string
    }
  }
  report: {
    markdown: string
    summary: string
    recommendation: string
  }
  docx_filename?: string
  docx_download_url?: string
  chart_path?: string
}

export default function Home() {
  const [symbol, setSymbol] = useState('')
  const [timeframe, setTimeframe] = useState('1d')
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  const timeframes = [
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1wk', label: '1 Week' },
  ]

  const quickSelectStocks = [
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
    'TATAMOTORS', 'WIPRO', 'SBIN', 'BHARTIARTL', 'ITC'
  ]

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!symbol.trim()) {
      setError('Please enter a stock symbol')
      return
    }

    setLoading(true)
    setError(null)
    setAnalysisData(null)

    try {
      // Call backend directly to avoid Vercel proxy timeout (10s limit)
      const response = await fetch(`${API_URL}/api/analyze-ai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          symbol: symbol.toUpperCase().trim(), 
          timeframe 
        }),
      })

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        console.error('Non-JSON response:', text)
        throw new Error(`Server returned non-JSON response. Please check if the backend is running correctly.`)
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail || 
          errorData.message || 
          errorData.error ||
          `Analysis failed with status ${response.status}`
        )
      }

      const data = await response.json()
      
      if (data.status === 'error') {
        throw new Error(data.message || 'Analysis failed')
      }
      
      setAnalysisData(data)
      setActiveTab('overview')
    } catch (err) {
      console.error('Analysis error:', err)
      
      // Provide helpful error messages
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Cannot connect to the analysis server. Please check if the backend is running.')
      } else if (err instanceof Error && err.message.includes('Failed to fetch')) {
        setError('Network error. The backend server may be starting up (takes ~60 seconds on first request). Please try again.')
      } else {
        setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadDocx = () => {
    if (analysisData?.docx_filename) {
      // Use direct backend URL for download
      const downloadUrl = `${API_URL}/api/download/docx/${analysisData.docx_filename}`
      window.open(downloadUrl, '_blank')
    }
  }

  const getRecommendationColor = (recommendation: string) => {
    const rec = recommendation.toUpperCase()
    if (rec.includes('BUY') || rec.includes('BULLISH')) {
      return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700'
    } else if (rec.includes('SELL') || rec.includes('BEARISH')) {
      return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-300 dark:border-red-700'
    } else {
      return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700'
    }
  }

  const getBiasIcon = (bias: string) => {
    const b = bias.toUpperCase()
    if (b.includes('BULLISH')) {
      return <TrendingUp className="h-5 w-5 text-green-500" />
    } else if (b.includes('BEARISH')) {
      return <TrendingDown className="h-5 w-5 text-red-500" />
    }
    return <BarChart3 className="h-5 w-5 text-yellow-500" />
  }

  const getConfidenceColor = (confidence: string) => {
    const c = confidence.toUpperCase()
    if (c === 'HIGH') return 'text-green-600 dark:text-green-400'
    if (c === 'MODERATE' || c === 'MEDIUM') return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Analysis Form */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 mb-8">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">
            Stock Technical Analysis
          </h2>
          
          <form onSubmit={handleAnalyze} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Stock Symbol Input */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Stock Symbol (NSE)
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="e.g., RELIANCE, TCS, INFY"
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                />
              </div>

              {/* Timeframe Select */}
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Timeframe
                </label>
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  disabled={loading}
                >
                  {timeframes.map((tf) => (
                    <option key={tf.value} value={tf.value}>
                      {tf.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Quick Select Buttons */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Quick Select
              </label>
              <div className="flex flex-wrap gap-2">
                {quickSelectStocks.map((stock) => (
                  <button
                    key={stock}
                    type="button"
                    onClick={() => setSymbol(stock)}
                    disabled={loading}
                    className={`px-3 py-1.5 text-sm rounded-lg border transition ${
                      symbol === stock
                        ? 'bg-blue-500 text-white border-blue-500'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-600 hover:bg-slate-200 dark:hover:bg-slate-600'
                    } disabled:opacity-50`}
                  >
                    {stock}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !symbol.trim()}
              className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing... (30-60s)
                </>
              ) : (
                <>
                  <BarChart3 className="h-5 w-5" />
                  Analyze Stock
                </>
              )}
            </button>
          </form>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-700 dark:text-red-300 font-medium">Analysis Failed</p>
                <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {analysisData && (
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden">
            {/* Results Header */}
            <div className="p-6 border-b border-slate-200 dark:border-slate-700">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h3 className="text-2xl font-bold text-slate-800 dark:text-white">
                    {analysisData.symbol} Analysis
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400">
                    {analysisData.stock_info?.company_name || analysisData.symbol} • {analysisData.timeframe} timeframe
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
                  {/* Recommendation Badge */}
                  <span className={`px-4 py-2 rounded-lg font-semibold border ${getRecommendationColor(analysisData.report?.recommendation || '')}`}>
                    {analysisData.report?.recommendation || 'N/A'}
                  </span>
                  
                  {/* Download Button */}
                  {analysisData.docx_filename && (
                    <button
                      onClick={handleDownloadDocx}
                      className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition"
                    >
                      <Download className="h-4 w-4" />
                      Download DOCX
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-slate-200 dark:border-slate-700">
              <div className="flex">
                {[
                  { id: 'overview', label: 'Overview', icon: BarChart3 },
                  { id: 'scenarios', label: 'Scenarios', icon: Target },
                  { id: 'report', label: 'Report', icon: FileText },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-6 py-4 font-medium transition ${
                      activeTab === tab.id
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
                    }`}
                  >
                    <tab.icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Bias */}
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        {getBiasIcon(analysisData.technical_analysis?.overall_bias || '')}
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Overall Bias</span>
                      </div>
                      <p className="text-xl font-bold text-slate-800 dark:text-white">
                        {analysisData.technical_analysis?.overall_bias || 'N/A'}
                      </p>
                    </div>

                    {/* Strength Score */}
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="h-5 w-5 text-blue-500" />
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Strength Score</span>
                      </div>
                      <p className="text-xl font-bold text-slate-800 dark:text-white">
                        {analysisData.technical_analysis?.strength_score?.toFixed(1) || 'N/A'}%
                      </p>
                    </div>

                    {/* Pattern Confidence */}
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="h-5 w-5 text-purple-500" />
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Pattern Confidence</span>
                      </div>
                      <p className={`text-xl font-bold ${getConfidenceColor(analysisData.pattern_analysis?.confidence || '')}`}>
                        {analysisData.pattern_analysis?.confidence || 'N/A'}
                      </p>
                    </div>

                    {/* Current Price */}
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-5 w-5 text-green-500" />
                        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Current Price</span>
                      </div>
                      <p className="text-xl font-bold text-slate-800 dark:text-white">
                        ₹{analysisData.latest_candle?.close?.toFixed(2) || 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Summary */}
                  {analysisData.report?.summary && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Summary</h4>
                      <p className="text-blue-700 dark:text-blue-200">{analysisData.report.summary}</p>
                    </div>
                  )}

                  {/* Key Levels */}
                  {analysisData.technical_analysis?.key_levels && (
                    <div>
                      <h4 className="font-semibold text-slate-800 dark:text-white mb-3">Key Levels</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {analysisData.technical_analysis.key_levels.resistance_2 && (
                          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                            <p className="text-xs text-red-600 dark:text-red-400">Resistance 2</p>
                            <p className="text-lg font-bold text-red-700 dark:text-red-300">
                              ₹{analysisData.technical_analysis.key_levels.resistance_2.toFixed(2)}
                            </p>
                          </div>
                        )}
                        {analysisData.technical_analysis.key_levels.resistance_1 && (
                          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                            <p className="text-xs text-red-600 dark:text-red-400">Resistance 1</p>
                            <p className="text-lg font-bold text-red-700 dark:text-red-300">
                              ₹{analysisData.technical_analysis.key_levels.resistance_1.toFixed(2)}
                            </p>
                          </div>
                        )}
                        {analysisData.technical_analysis.key_levels.support_1 && (
                          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                            <p className="text-xs text-green-600 dark:text-green-400">Support 1</p>
                            <p className="text-lg font-bold text-green-700 dark:text-green-300">
                              ₹{analysisData.technical_analysis.key_levels.support_1.toFixed(2)}
                            </p>
                          </div>
                        )}
                        {analysisData.technical_analysis.key_levels.support_2 && (
                          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                            <p className="text-xs text-green-600 dark:text-green-400">Support 2</p>
                            <p className="text-lg font-bold text-green-700 dark:text-green-300">
                              ₹{analysisData.technical_analysis.key_levels.support_2.toFixed(2)}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Patterns */}
                  {analysisData.pattern_analysis?.patterns && analysisData.pattern_analysis.patterns.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-slate-800 dark:text-white mb-3">Detected Patterns</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysisData.pattern_analysis.patterns.map((pattern, index) => (
                          <span
                            key={index}
                            className="px-3 py-1.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg text-sm"
                          >
                            {pattern.pattern} ({pattern.confidence})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Scenarios Tab */}
              {activeTab === 'scenarios' && (
                <div className="space-y-6">
                  {analysisData.risk_analysis?.scenarios && analysisData.risk_analysis.scenarios.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-slate-200 dark:border-slate-700">
                            <th className="text-left py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">Scenario</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">Entry</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">Stop</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">Target</th>
                            <th className="text-right py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">R:R</th>
                            <th className="text-center py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">Confidence</th>
                          </tr>
                        </thead>
                        <tbody>
                          {analysisData.risk_analysis.scenarios.map((scenario, index) => (
                            <tr key={index} className="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                              <td className="py-3 px-4">
                                <div>
                                  <p className="font-medium text-slate-800 dark:text-white">{scenario.scenario}</p>
                                  {scenario.warreni_take && (
                                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{scenario.warreni_take}</p>
                                  )}
                                </div>
                              </td>
                              <td className="text-right py-3 px-4 text-slate-800 dark:text-white">₹{scenario.entry?.toFixed(2)}</td>
                              <td className="text-right py-3 px-4 text-red-600 dark:text-red-400">₹{scenario.stop?.toFixed(2)}</td>
                              <td className="text-right py-3 px-4 text-green-600 dark:text-green-400">₹{scenario.target?.toFixed(2)}</td>
                              <td className="text-right py-3 px-4">
                                <span className={`font-bold ${scenario.rr_ratio >= 2 ? 'text-green-600 dark:text-green-400' : scenario.rr_ratio >= 1.5 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'}`}>
                                  {scenario.rr_ratio?.toFixed(2)}
                                </span>
                              </td>
                              <td className="text-center py-3 px-4">
                                <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(scenario.confidence)}`}>
                                  {scenario.confidence}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-slate-600 dark:text-slate-400">No scenarios available.</p>
                  )}

                  {/* Risk Metrics */}
                  {analysisData.risk_analysis?.risk_metrics && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                        <p className="text-sm text-slate-600 dark:text-slate-400">Avg R:R Ratio</p>
                        <p className="text-xl font-bold text-slate-800 dark:text-white">
                          {analysisData.risk_analysis.risk_metrics.average_rr_ratio?.toFixed(2) || 'N/A'}
                        </p>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                        <p className="text-sm text-slate-600 dark:text-slate-400">Volatility</p>
                        <p className="text-xl font-bold text-slate-800 dark:text-white">
                          {analysisData.risk_analysis.risk_metrics.volatility_level || 'N/A'}
                        </p>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                        <p className="text-sm text-slate-600 dark:text-slate-400">Risk Grade</p>
                        <p className="text-xl font-bold text-slate-800 dark:text-white">
                          {analysisData.risk_analysis.risk_metrics.risk_grade || 'N/A'}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Position Sizing */}
                  {analysisData.risk_analysis?.position_sizing && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mt-4">
                      <h4 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Position Sizing</h4>
                      <p className="text-blue-700 dark:text-blue-200">
                        <strong>Recommended:</strong> {analysisData.risk_analysis.position_sizing.recommended_position}
                      </p>
                      {analysisData.risk_analysis.position_sizing.rationale && (
                        <p className="text-sm text-blue-600 dark:text-blue-300 mt-1">
                          {analysisData.risk_analysis.position_sizing.rationale}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Report Tab */}
              {activeTab === 'report' && (
                <div className="prose prose-slate dark:prose-invert max-w-none">
                  {analysisData.report?.markdown ? (
                    <ReactMarkdown>{analysisData.report.markdown}</ReactMarkdown>
                  ) : (
                    <p className="text-slate-600 dark:text-slate-400">No report available.</p>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-slate-50 dark:bg-slate-700/50 border-t border-slate-200 dark:border-slate-700">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 text-sm text-slate-600 dark:text-slate-400">
                <span>
                  Analysis completed in {analysisData.execution_time?.toFixed(1)}s
                </span>
                <span>
                  Generated by 5 AI Agents • {new Date().toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
