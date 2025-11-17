'use client'

import { useState, useEffect } from 'react'
import { Moon, Sun, TrendingUp } from 'lucide-react'

export function Header() {
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    // Check for saved preference or system preference
    const isDark = localStorage.getItem('darkMode') === 'true' ||
      (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    
    setDarkMode(isDark)
    document.documentElement.classList.toggle('dark', isDark)
  }, [])

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    localStorage.setItem('darkMode', newMode.toString())
    document.documentElement.classList.toggle('dark', newMode)
  }

  return (
    <header className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-7xl">
        <div className="flex items-center space-x-2">
          <div className="bg-primary rounded-lg p-2">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white">
            Stock Analysis AI
          </span>
        </div>

        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle dark mode"
        >
          {darkMode ? (
            <Sun className="h-5 w-5 text-slate-600 dark:text-slate-300" />
          ) : (
            <Moon className="h-5 w-5 text-slate-600" />
          )}
        </button>
      </div>
    </header>
  )
}
