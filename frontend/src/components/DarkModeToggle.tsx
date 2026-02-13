'use client'

import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { motion } from 'framer-motion'

export function DarkModeToggle() {
  const [mounted, setMounted] = useState(false)
  const [isDark, setIsDark] = useState(false)

  // Only run on client after mount
  useEffect(() => {
    setMounted(true)
    const stored = localStorage.getItem('theme')
    if (stored) {
      setIsDark(stored === 'dark')
    } else {
      setIsDark(window.matchMedia('(prefers-color-scheme: dark)').matches)
    }
  }, [])

  useEffect(() => {
    if (!mounted) return
    
    // Apply theme
    const root = document.documentElement
    if (isDark) {
      root.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      root.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark, mounted])

  const handleToggle = () => {
    setIsDark(prev => !prev)
  }

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="relative w-14 h-7 bg-slate-700 rounded-full p-1">
        <div className="w-5 h-5 bg-white rounded-full" />
      </div>
    )
  }

  return (
    <button
      onClick={handleToggle}
      className="relative w-14 h-7 bg-slate-700 rounded-full p-1 transition-colors hover:bg-slate-600"
      aria-label="Toggle dark mode"
    >
      <motion.div
        className="w-5 h-5 bg-white rounded-full flex items-center justify-center"
        animate={{ x: isDark ? 24 : 0 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      >
        {isDark ? (
          <Sun size={12} className="text-amber-500" />
        ) : (
          <Moon size={12} className="text-slate-900" />
        )}
      </motion.div>
    </button>
  )
}
