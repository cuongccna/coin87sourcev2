'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { Star, Heart, TrendingUp, Plus, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface FeedSwitcherProps {
  currentType: 'for_you' | 'watchlist_only'
  onChange: (type: 'for_you' | 'watchlist_only') => void
}

export function FeedSwitcher({ currentType, onChange }: FeedSwitcherProps) {
  return (
    <div className="flex gap-2 p-1 bg-slate-800 rounded-lg w-fit">
      <button
        onClick={() => onChange('for_you')}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
          currentType === 'for_you'
            ? 'bg-primary text-slate-900'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <div className="flex items-center gap-2">
          <TrendingUp size={16} />
          <span>For You</span>
        </div>
      </button>
      <button
        onClick={() => onChange('watchlist_only')}
        className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
          currentType === 'watchlist_only'
            ? 'bg-primary text-slate-900'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <div className="flex items-center gap-2">
          <Star size={16} />
          <span>Watchlist</span>
        </div>
      </button>
    </div>
  )
}

interface WatchlistModalProps {
  isOpen: boolean
  onClose: () => void
  userWatchlist: string[]
  onUpdate: () => void
}

const fetcher = (url: string) =>
  fetch(url, { credentials: 'include' }).then((r) => r.json())

export function WatchlistModal({
  isOpen,
  onClose,
  userWatchlist,
  onUpdate,
}: WatchlistModalProps) {
  const [search, setSearch] = useState('')
  const [watchlist, setWatchlist] = useState(userWatchlist)

  const { data: coins } = useSWR<string[]>(
    isOpen ? '/api/v1/coins/search?q=' + search : null,
    fetcher
  )

  const toggleCoin = async (coin: string) => {
    const isAdding = !watchlist.includes(coin)
    const newWatchlist = isAdding
      ? [...watchlist, coin]
      : watchlist.filter((c) => c !== coin)

    setWatchlist(newWatchlist)

    try {
      await fetch('/api/v1/users/me/watchlist', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ watchlist: newWatchlist }),
      })
      onUpdate()
    } catch (error) {
      console.error('Failed to update watchlist:', error)
      // Rollback
      setWatchlist(userWatchlist)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-x-4 top-20 max-w-lg mx-auto bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl z-50 max-h-[80vh] overflow-hidden flex flex-col"
          >
            <div className="flex items-center justify-between p-6 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-slate-100">Watchlist</h2>
                <p className="text-sm text-slate-500 mt-1">
                  {watchlist.length} coins tracked
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X size={20} className="text-slate-400" />
              </button>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-slate-800">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search coins (BTC, ETH, SOL...)"
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Current Watchlist */}
            <div className="flex-1 overflow-y-auto p-4">
              {watchlist.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Heart size={48} className="mx-auto mb-3 opacity-50" />
                  <p>No coins in watchlist</p>
                  <p className="text-xs mt-1">Search and add coins above</p>
                </div>
              ) : (
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-slate-400 mb-2">
                    YOUR WATCHLIST
                  </h3>
                  {watchlist.map((coin) => (
                    <motion.div
                      key={coin}
                      layout
                      className="flex items-center justify-between p-3 bg-slate-800 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                          <span className="text-xs font-bold text-primary">
                            {coin.slice(0, 2)}
                          </span>
                        </div>
                        <span className="font-medium text-slate-100">{coin}</span>
                      </div>
                      <button
                        onClick={() => toggleCoin(coin)}
                        className="p-1.5 hover:bg-slate-700 rounded transition-colors"
                      >
                        <X size={16} className="text-slate-400" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              )}

              {/* Search Results */}
              {search && coins && coins.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h3 className="text-sm font-medium text-slate-400 mb-2">
                    SEARCH RESULTS
                  </h3>
                  {coins
                    .filter((coin) => !watchlist.includes(coin))
                    .map((coin) => (
                      <motion.div
                        key={coin}
                        layout
                        className="flex items-center justify-between p-3 bg-slate-800 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-slate-400">
                              {coin.slice(0, 2)}
                            </span>
                          </div>
                          <span className="font-medium text-slate-100">{coin}</span>
                        </div>
                        <button
                          onClick={() => toggleCoin(coin)}
                          className="p-1.5 hover:bg-slate-700 rounded transition-colors"
                        >
                          <Plus size={16} className="text-primary" />
                        </button>
                      </motion.div>
                    ))}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
