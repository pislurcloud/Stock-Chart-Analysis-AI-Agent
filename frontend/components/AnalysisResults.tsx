'use client'

import { useState } from 'react'
import { Download, FileText, BarChart3, Target, AlertTriangle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ScenarioTable } from './ScenarioTable'
import { MetricsCard } from './MetricsCard'

interface AnalysisResultsProps {
  data: any
}

export function AnalysisResults({ data }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState('overview')

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'scenarios', label: 'Scenarios', icon: Target },
    { id: 'report', label: 'Full Report', icon: FileText },
  ]

  const handleDownload = async () => {
    if (data.docx_download_url) {
      try {
        const response = await fetch(data.docx_download_url)
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.docx_filename || 'analysis_report.docx'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } catch (error) {
        console.error('Download failed:', error)
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
              {data.stock_info.company_name}
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 mt-1">
              {data.symbol} • {data.timeframe.toUpperCase()}
            </p>
          </div>

          <div className="flex flex-col items-start md:items-end gap-2">
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Current Price:
              </span>
              <span className="text-2xl font-bold text-slate-900 dark:text-white">
                ₹{data.latest_candle.close.toFixed(2)}
              </span>
            </div>
            
            <div className={`px-4 py-2 rounded-full font-semibold ${
              data.report.recommendation.includes('BUY')
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                : data.report.recommendation.includes('WAIT')
                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
            }`}>
              {data.report.recommendation}
            </div>

            {data.docx_download_url && (
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg transition-all shadow-md hover:shadow-lg"
              >
                <Download className="h-4 w-4" />
                Download DOCX Report
              </button>
            )}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <MetricsCard
            label="Technical Bias"
            value={data.technical_analysis.overall_bias}
            className={
              data.technical_analysis.overall_bias.includes('BULLISH')
                ? 'text-green-600 dark:text-green-400'
                : data.technical_analysis.overall_bias.includes('BEARISH')
                ? 'text-red-600 dark:text-red-400'
                : 'text-slate-600 dark:text-slate-400'
            }
          />
          <MetricsCard
            label="Signal Strength"
            value={`${data.technical_analysis.strength_score}/100`}
          />
          <MetricsCard
            label="Market Structure"
            value={data.pattern_analysis.market_structure}
          />
          <MetricsCard
            label="Execution Time"
            value={`${data.execution_time.toFixed(1)}s`}
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
        {/* Tab Headers */}
        <div className="flex border-b border-slate-200 dark:border-slate-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-primary text-white'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            >
              <tab.icon className="h-5 w-5" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Summary */}
              <div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-3">
                  Executive Summary
                </h3>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {data.report.summary}
                </p>
              </div>

              {/* Key Levels */}
              <div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-3">
                  Key Price Levels
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {Object.entries(data.technical_analysis.key_levels).map(([key, value]: [string, any]) => (
                    <div key={key} className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                      <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                        {key.replace('_', ' ').toUpperCase()}
                      </div>
                      <div className="text-lg font-semibold text-slate-900 dark:text-white">
                        ₹{typeof value === 'number' ? value.toFixed(2) : value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'scenarios' && (
            <div className="space-y-6">
              <div className="flex items-start gap-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <AlertTriangle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                    Trading Scenarios
                  </h4>
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    AI-generated entry, stop loss, and target levels with risk/reward ratios.
                    Always do your own research before trading.
                  </p>
                </div>
              </div>

              <ScenarioTable scenarios={data.risk_analysis.scenarios} />

              {/* Position Sizing */}
              <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
                  Position Sizing Recommendation
                </h4>
                <p className="text-slate-700 dark:text-slate-300">
                  <strong>Recommended:</strong> {data.risk_analysis.position_sizing.recommended_position}
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  {data.risk_analysis.position_sizing.rationale}
                </p>
              </div>

              {/* Backtest */}
              {data.risk_analysis.backtest && (
                <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                  <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
                    Backtest Results
                  </h4>
                  <p className="text-slate-700 dark:text-slate-300">
                    Estimated Success Rate: <strong>{data.risk_analysis.backtest.estimated_success_rate}%</strong>
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {data.risk_analysis.backtest.note}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'report' && (
            <div className="prose prose-slate dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {data.report.markdown}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
