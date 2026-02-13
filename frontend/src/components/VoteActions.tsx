"use client";

import React, { useState, useEffect } from "react";
import { useTranslations } from 'next-intl';
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";
import toast from "react-hot-toast";


interface VoteActionsProps {
  newsId: number;
  initialVote?: 'trust' | 'fake' | null;
}

export const VoteActions: React.FC<VoteActionsProps> = ({ newsId, initialVote = null }) => {
  const [vote, setVote] = useState<'trust' | 'fake' | null>(initialVote);
  const [showReward, setShowReward] = useState(false);
  const [reward, setReward] = useState(0);
  const [loading, setLoading] = useState(true);
  const { apiKey } = useAuth();
  const t = useTranslations('news');

  // Fetch vote status on mount
  useEffect(() => {
    const checkVoteStatus = async () => {
      if (!apiKey) {
        setLoading(false)
        return
      }
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010'}/api/v1/news/${newsId}/vote-status`, {
          headers: { 'X-API-KEY': apiKey }
        })
        if (res.ok) {
          const data = await res.json()
          if (data.has_voted) {
            setVote(data.vote_type)
          }
        }
      } catch (error) {
        console.error('Failed to check vote status:', error)
      } finally {
        setLoading(false)
      }
    }
    checkVoteStatus()
  }, [newsId, apiKey])

  const handleVote = async (type: 'trust' | 'fake') => {
    if (vote !== null) {
      toast.error(t('vote.alreadyVoted'));
      return;
    }
    if (!apiKey) {
      toast.error(t('vote.loginRequired'));
      return;
    }

    // 1. Optimistic UI
    setVote(type);
    setShowReward(true);

    // 2. Haptic Feedback
    if (typeof navigator !== "undefined" && navigator.vibrate) {
      navigator.vibrate(50);
    }

    // 3. API Call
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010'}/api/v1/news/${newsId}/vote`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-KEY': apiKey
        },
        body: JSON.stringify({ vote_type: type })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Vote failed' }));
        throw new Error(errData.detail || 'Vote failed');
      }

      const data = await res.json();
      setReward(data.reward || 0.1);
      toast.success(t('vote.voteSuccess', { tokens: (data.reward || 0).toFixed(2) }));
    } catch (error) {
      console.error('Vote failed', error);
      // Revert optimism
      setVote(null);
      setShowReward(false);
      toast.error(error instanceof Error ? error.message : t('vote.voteFailed'));
      return;
    }

    // Hide reward after animation
    setTimeout(() => setShowReward(false), 2000);
  };

  return (
    <div className="flex items-center gap-2 sm:gap-3 mt-3 relative">
      {/* Trust Button */}
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={() => handleVote('trust')}
        disabled={vote !== null}
        className={cn(
          "flex-1 flex items-center justify-center gap-1.5 sm:gap-2 py-2 rounded-lg font-bold text-xs sm:text-sm transition-all relative overflow-hidden",
          vote === 'trust' 
            ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/50"
            : vote === 'fake'
            ? "bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 opacity-50 cursor-not-allowed"
            : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-green-50 dark:hover:bg-slate-700 hover:text-green-600 dark:hover:text-green-400 border border-slate-300 dark:border-slate-700"
        )}
      >
        <ThumbsUp className={cn("w-3.5 h-3.5 sm:w-4 sm:h-4", vote === 'trust' && "fill-current")} />
        <span className="hidden sm:inline">Trust</span>
      </motion.button>

      {/* Fake Button */}
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={() => handleVote('fake')}
        disabled={vote !== null}
        className={cn(
          "flex-1 flex items-center justify-center gap-1.5 sm:gap-2 py-2 rounded-lg font-bold text-xs sm:text-sm transition-all",
          vote === 'fake'
            ? "bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/50"
            : vote === 'trust'
            ? "bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 opacity-50 cursor-not-allowed"
            : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-slate-700 hover:text-red-600 dark:hover:text-red-400 border border-slate-300 dark:border-slate-700"
        )}
      >
        <ThumbsDown className={cn("w-3.5 h-3.5 sm:w-4 sm:h-4", vote === 'fake' && "fill-current")} />
        <span className="hidden sm:inline">Fake</span>
      </motion.button>

      {/* Floating Reward Animation */}
      <AnimatePresence>
        {showReward && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.5 }}
            animate={{ opacity: 1, y: -20, scale: 1 }}
            exit={{ opacity: 0, y: -40 }}
            className="absolute left-1/2 transform -translate-x-1/2 pointer-events-none z-50 text-yellow-500 dark:text-yellow-400 font-black text-base sm:text-lg drop-shadow-md"
          >
            +{reward.toFixed(2)} $C87
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

