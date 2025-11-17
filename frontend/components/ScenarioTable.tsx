'use client'

interface Scenario {
  scenario: string
  entry: number
  stop: number
  target: number
  rr_ratio: number
  confidence: string
  warreni_take: string
}

interface ScenarioTableProps {
  scenarios: Scenario[]
}

export function ScenarioTable({ scenarios }: ScenarioTableProps) {
  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
      case 'moderate':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
      case 'low':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
      default:
        return 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
    }
  }

  const getRRColor = (rr: number) => {
    if (rr >= 2) return 'text-green-600 dark:text-green-400 font-bold'
    if (rr >= 1) return 'text-blue-600 dark:text-blue-400 font-semibold'
    return 'text-red-600 dark:text-red-400'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-slate-100 dark:bg-slate-700">
            <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              Scenario
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              Entry
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              Stop
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              Target
            </th>
            <th className="px-4 py-3 text-right text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              R:R
            </th>
            <th className="px-4 py-3 text-center text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              Confidence
            </th>
            <th className="px-4 py-3 text-left text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-600">
              WarrenAI Take
            </th>
          </tr>
        </thead>
        <tbody>
          {scenarios.map((scenario, index) => (
            <tr
              key={index}
              className="border-b border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
            >
              <td className="px-4 py-3 text-sm font-medium text-slate-900 dark:text-white">
                {scenario.scenario}
              </td>
              <td className="px-4 py-3 text-sm text-right text-slate-700 dark:text-slate-300">
                ₹{scenario.entry.toFixed(2)}
              </td>
              <td className="px-4 py-3 text-sm text-right text-slate-700 dark:text-slate-300">
                ₹{scenario.stop.toFixed(2)}
              </td>
              <td className="px-4 py-3 text-sm text-right text-slate-700 dark:text-slate-300">
                ₹{scenario.target.toFixed(2)}
              </td>
              <td className={`px-4 py-3 text-sm text-right ${getRRColor(scenario.rr_ratio)}`}>
                {scenario.rr_ratio.toFixed(2)}
              </td>
              <td className="px-4 py-3 text-center">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(scenario.confidence)}`}>
                  {scenario.confidence}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400 max-w-xs">
                {scenario.warreni_take}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
