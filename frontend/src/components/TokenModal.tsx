'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { X, Wallet, TrendingUp, TrendingDown, Lock, Zap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { useAuth } from '@/context/AuthContext'

interface Transaction {
  id: string
  transaction_type: 'EARN_VOTE' | 'SPEND_UNLOCK' | 'SPEND_BOOST'
  amount: number
  news_id?: string
  created_at: string
}

interface TokenModalProps {
  isOpen: boolean
  onClose: () => void
  currentBalance: number
  newsId?: string
  action?: string
}

export function TokenModal({ isOpen, onClose, currentBalance, newsId, action }: TokenModalProps) {
  const { apiKey } = useAuth()
  
  const fetcher = (url: string) =>
    fetch(url, { 
      headers: apiKey ? { 'X-API-KEY': apiKey } : {},
      credentials: 'include' 
    }).then((r) => r.json())

  const { data: transactions, mutate } = useSWR<Transaction[]>(
    isOpen ? (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010') + '/api/v1/economy/transactions' : null,
    fetcher
  )

  const handleSpend = async (type: 'unlock' | 'boost', spendNewsId?: string) => {
    if (!apiKey) {
      toast.error('Please login to spend tokens')
      return
    }

    const targetNewsId = spendNewsId || newsId

    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010') + '/api/v1/economy/spend', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-KEY': apiKey
        },
        credentials: 'include',
        body: JSON.stringify({
          spend_type: type,
          news_id: targetNewsId,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        mutate()
        toast.success(`Spent ${type === 'boost' ? '100' : '50'} $C87 successfully!`)
        
        // Dispatch unlock success event for NewsCard
        if (type === 'unlock' && targetNewsId) {
          window.dispatchEvent(new CustomEvent('unlockSuccess', { 
            detail: { newsId: targetNewsId } 
          }))
        }
        
        // Refresh user balance
        setTimeout(() => window.location.reload(), 1000)
      } else {
        const error = await res.json().catch(() => ({ detail: 'Failed to spend tokens' }))
        toast.error(error.detail || 'Failed to spend tokens')
      }
    } catch (error) {
      console.error('Spend error:', error)
      toast.error('Failed to spend tokens')
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-x-4 top-20 max-w-lg mx-auto bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl z-50 max-h-[80vh] overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Token Economy</h2>
                <div className="flex items-center gap-2 mt-1">
                  <Wallet className="w-5 h-5 text-yellow-500 dark:text-primary" />
                  <span className="text-2xl font-bold text-yellow-500 dark:text-primary">
                    {currentBalance.toFixed(2)}
                  </span>
                  <span className="text-sm text-slate-500">$C87</span>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X size={20} className="text-slate-500 dark:text-slate-400" />
              </button>
            </div>

            {/* Spend Options */}
            <div className="p-6 space-y-3 border-b border-slate-200 dark:border-slate-800">
              <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">SPEND TOKENS</h3>
              
              <motion.button
                onClick={() => handleSpend('boost')}
                className="w-full flex items-center justify-between p-4 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-300 dark:border-slate-700"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-yellow-400/20 dark:bg-primary/20 rounded-full flex items-center justify-center">
                    <Zap size={20} className="text-yellow-500 dark:text-primary" />
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-slate-900 dark:text-slate-100">Boost News</p>
                    <p className="text-xs text-slate-500">Increase visibility for 24h</p>
                  </div>
                </div>
                <span className="text-yellow-500 dark:text-primary font-bold">100 $C87</span>
              </motion.button>

              <motion.button
                onClick={() => handleSpend('unlock')}
                className="w-full flex items-center justify-between p-4 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-300 dark:border-slate-700"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <Lock size={20} className="text-blue-400" />
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-slate-900 dark:text-slate-100">Unlock News</p>
                    <p className="text-xs text-slate-500">Access full analysis</p>
                  </div>
                </div>
                <span className="text-yellow-500 dark:text-primary font-bold">50 $C87</span>
              </motion.button>
            </div>

            {/* Transaction History */}
            <div className="flex-1 overflow-y-auto p-6">
              <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-3">RECENT TRANSACTIONS</h3>
              
              {!transactions ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-slate-200 dark:bg-slate-800 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : transactions.length === 0 ? (
                <p className="text-center text-slate-500 py-8">No transactions yet</p>
              ) : (
                <div className="space-y-2">
                  {transactions.map((tx) => (
                    <div
                      key={tx.id}
                      className="flex items-center justify-between p-3 bg-slate-100 dark:bg-slate-800 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            tx.transaction_type === 'EARN_VOTE'
                              ? 'bg-emerald-500/20'
                              : 'bg-red-500/20'
                          }`}
                        >
                          {tx.transaction_type === 'EARN_VOTE' ? (
                            <TrendingUp size={16} className="text-emerald-400" />
                          ) : (
                            <TrendingDown size={16} className="text-red-400" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                            {tx.transaction_type === 'EARN_VOTE' && 'Vote Reward'}
                            {tx.transaction_type === 'SPEND_UNLOCK' && 'Unlock News'}
                            {tx.transaction_type === 'SPEND_BOOST' && 'Boost News'}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {new Date(tx.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <span
                        className={`font-bold ${
                          tx.amount > 0 ? 'text-emerald-400' : 'text-red-400'
                        }`}
                      >
                        {tx.amount > 0 ? '+' : ''}
                        {tx.amount}
                      </span>
                    </div>
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
