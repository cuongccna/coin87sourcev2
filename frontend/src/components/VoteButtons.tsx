'use client'

import { useState } from 'react'
import { ThumbsUp, ThumbsDown, Shield, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'

interface VoteButtonsProps {
  newsId: string
  initialTrustCount: number
  initialFakeCount: number
  userVote?: 'trust' | 'fake' | null
  onVoteSuccess?: () => void
}

export function VoteButtons({
  newsId,
  initialTrustCount,
  initialFakeCount,
  userVote: initialUserVote,
  onVoteSuccess,
}: VoteButtonsProps) {
  const [trustCount, setTrustCount] = useState(initialTrustCount)
  const [fakeCount, setFakeCount] = useState(initialFakeCount)
  const [userVote, setUserVote] = useState(initialUserVote)
  const [loading, setLoading] = useState(false)

  const totalVotes = trustCount + fakeCount
  const trustPercentage = totalVotes > 0 ? (trustCount / totalVotes) * 100 : 50
  const credibilityScore = totalVotes > 0 ? trustPercentage / 100 : 0.5

  const handleVote = async (voteType: 'trust' | 'fake') => {
    if (loading) return

    setLoading(true)
    try {
      const res = await fetch(`/api/v1/news/${newsId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ vote_type: voteType }),
      })

      if (res.status === 401) {
        // Redirect to login
        window.location.href = '/login'
        return
      }

      if (res.ok) {
        const data = await res.json()
        
        // Update counts
        setTrustCount(data.trust_count)
        setFakeCount(data.fake_count)
        setUserVote(voteType)
        
        onVoteSuccess?.()
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to vote')
      }
    } catch (error) {
      console.error('Vote failed:', error)
      alert('Failed to vote. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      {/* Credibility Score Bar */}
      <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`absolute left-0 top-0 h-full ${
            credibilityScore >= 0.7
              ? 'bg-emerald-500'
              : credibilityScore >= 0.4
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${trustPercentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      {/* Vote Buttons */}
      <div className="flex gap-2">
        <motion.button
          onClick={() => handleVote('trust')}
          disabled={loading || userVote === 'trust'}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
            userVote === 'trust'
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
              : 'bg-slate-800 text-slate-300 hover:bg-emerald-500/20 hover:text-emerald-400 border border-slate-700 hover:border-emerald-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          whileTap={{ scale: 0.95 }}
          whileHover={{ scale: 1.02 }}
        >
          <Shield size={18} />
          <span>Trust</span>
          <span className="text-sm opacity-80">{trustCount}</span>
        </motion.button>

        <motion.button
          onClick={() => handleVote('fake')}
          disabled={loading || userVote === 'fake'}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
            userVote === 'fake'
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/20'
              : 'bg-slate-800 text-slate-300 hover:bg-red-500/20 hover:text-red-400 border border-slate-700 hover:border-red-500'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          whileTap={{ scale: 0.95 }}
          whileHover={{ scale: 1.02 }}
        >
          <AlertTriangle size={18} />
          <span>Fake</span>
          <span className="text-sm opacity-80">{fakeCount}</span>
        </motion.button>
      </div>

      {/* Credibility Status */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-1">
          {credibilityScore >= 0.7 ? (
            <>
              <Shield size={12} className="text-emerald-500" />
              <span className="text-emerald-400">Highly Credible</span>
            </>
          ) : credibilityScore >= 0.4 ? (
            <>
              <AlertTriangle size={12} className="text-yellow-500" />
              <span className="text-yellow-400">Mixed Reviews</span>
            </>
          ) : (
            <>
              <AlertTriangle size={12} className="text-red-500" />
              <span className="text-red-400">Low Credibility</span>
            </>
          )}
        </div>
        <span>{totalVotes} votes</span>
      </div>

      {/* Reward Info */}
      {!userVote && (
        <div className="text-xs text-center text-slate-500">
          Vote to earn <span className="text-primary font-medium">+5 $C87</span>
        </div>
      )}
    </div>
  )
}
