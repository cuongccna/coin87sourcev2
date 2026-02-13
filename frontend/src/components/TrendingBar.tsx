'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, Flame, Zap } from 'lucide-react'
import { motion } from 'framer-motion'

interface Narrative {
  tag: string  // Backend returns 'tag', not 'narrative_name'
  velocity: number
  count_24h: number
  avg_daily_7d: number
}

export function TrendingBar() {
  const [narratives, setNarratives] = useState<Narrative[]>([])
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNarratives()
    const interval = setInterval(fetchNarratives, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchNarratives = async () => {
    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010') + '/api/v1/trends/narratives', {
        credentials: 'include',
      })
      if (res.ok) {
        const data = await res.json()
        setNarratives(data.slice(0, 10)) // Top 10 narratives
      }
    } catch (error) {
      console.error('Failed to fetch narratives:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleClick = (narrative: Narrative) => {
    setSelectedTag(narrative.tag === selectedTag ? null : narrative.tag)
    // Emit event for NewsFeed to filter
    window.dispatchEvent(
      new CustomEvent('filterByNarrative', {
        detail: narrative.tag === selectedTag ? null : narrative.tag,
      })
    )
  }

  if (loading) {
    return (
      <div className="sticky top-16 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="container mx-auto px-4 py-3">
          <div className="flex gap-2 overflow-hidden">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-8 w-32 bg-slate-200 dark:bg-slate-800 rounded-full animate-pulse"
              />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (narratives.length === 0) return null

  return (
    <div className="sticky top-16 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="container mx-auto px-4 py-2 sm:py-3">
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp size={14} className="text-yellow-500 dark:text-primary" />
          <span className="text-xs font-medium text-slate-600 dark:text-slate-400">TRENDING NOW</span>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {narratives.map((narrative, index) => (
            <motion.button
              key={narrative.tag || `narrative-${index}`}
              onClick={() => handleClick(narrative)}
              className={`flex-shrink-0 px-3 sm:px-4 py-2 rounded-full border transition-all text-sm ${
                selectedTag === narrative.tag
                  ? 'bg-yellow-500 border-yellow-500 text-slate-900 dark:bg-primary dark:border-primary'
                  : 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-yellow-500 dark:hover:border-primary'
              }`}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center gap-2">
                {/* Velocity indicator */}
                {narrative.velocity > 0.7 && (
                  <Flame size={14} className="text-orange-500" />
                )}
                {narrative.velocity > 0.5 && narrative.velocity <= 0.7 && (
                  <Zap size={14} className="text-yellow-500" />
                )}

                <span className="text-sm font-medium whitespace-nowrap">
                  {narrative.tag}
                </span>

                <span className="text-xs opacity-70">
                  {narrative.count_24h}
                </span>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  )
}
