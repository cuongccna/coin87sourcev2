"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { NewsItem } from "@/types";
import { useAuth } from "@/context/AuthContext";
import { Lock, TrendingUp, TrendingDown, Minus, ExternalLink, CheckCircle2, AlertCircle, XCircle, Shield, ShieldCheck } from "lucide-react";
import toast from "react-hot-toast";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
// import { vi } from "date-fns/locale"; // Vietnamese locale if needed
import { useTranslations } from 'next-intl';

import { VoteActions } from "./VoteActions";

interface NewsCardProps {
  news: NewsItem;
}

export const NewsCard: React.FC<NewsCardProps> = ({ news }) => {
  const { user } = useAuth();
  const t = useTranslations('news');
  const [isUnlocked, setIsUnlocked] = useState(false);
  const isPro = user?.tier === "Pro" || user?.tier === "Elite";
  
  // Check if paywall is enabled from environment variable
  const paywallEnabled = process.env.NEXT_PUBLIC_ENABLE_PAYWALL === 'true';
  
  // Auto unlock ONLY for Pro/Elite users (not based on balance)
  // OR if paywall is disabled globally
  useEffect(() => {
    if (!paywallEnabled || isPro) {
      setIsUnlocked(true);
    }
  }, [isPro, paywallEnabled]);

  // Listen for unlock success event from TokenModal
  useEffect(() => {
    const handleUnlockSuccess = (e: CustomEvent) => {
      if (e.detail.newsId === news.id) {
        console.log('Unlock success for news:', news.id);
        setIsUnlocked(true);
        toast.success('🔓 Unlocked! Enjoy reading');
      }
    };
    window.addEventListener('unlockSuccess' as any, handleUnlockSuccess);
    return () => window.removeEventListener('unlockSuccess' as any, handleUnlockSuccess);
  }, [news.id]);
  
  // Show content if: Pro user, unlocked this news, or has free quota
  const canViewContent = isPro || isUnlocked;

  // Get AI quality indicator
  const getAIQuality = () => {
    if (!news.summary_vi || news.summary_vi === t('card.aiUnavailable')) {
      return { label: t('card.aiQuality.noAI'), icon: XCircle, color: "text-red-500", bg: "bg-red-500/10" };
    }
    const len = news.summary_vi.length;
    if (len > 200) return { label: t('card.aiQuality.complete'), icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" };
    if (len > 100) return { label: t('card.aiQuality.partial'), icon: AlertCircle, color: "text-yellow-500", bg: "bg-yellow-500/10" };
    return { label: t('card.aiQuality.limited'), icon: AlertCircle, color: "text-orange-500", bg: "bg-orange-500/10" };
  };
  const aiQuality = getAIQuality();
  const AIIcon = aiQuality.icon;

  // Parse sentiment for color coding
  const getSentimentColor = (label?: string) => {
    switch (label) {
      case "Bullish":
        return "border-l-4 border-green-500";
      case "Bearish":
        return "border-l-4 border-red-500";
      default:
        return "border-l-4 border-gray-600";
    }
  };

  const getSentimentIcon = (label?: string) => {
      switch (label) {
        case "Bullish": return <TrendingUp className="w-4 h-4 text-green-500" />;
        case "Bearish": return <TrendingDown className="w-4 h-4 text-red-500" />;
        default: return <Minus className="w-4 h-4 text-gray-400" />;
      }
  }

  // Parse tags if string
  let tagsDisplay: string[] = [];
  if (Array.isArray(news.tags)) {
      tagsDisplay = news.tags;
  } else if (typeof news.tags === 'string') {
      try {
          tagsDisplay = JSON.parse(news.tags);
      } catch (e) {}
  }

  // Enhanced Trust Score styling
  const getTrustColor = (score?: number) => {
    if (!score) return { bg: "bg-gray-100 dark:bg-gray-800", text: "text-gray-600 dark:text-gray-400", icon: Shield };
    if (score >= 8) return { bg: "bg-green-100 dark:bg-green-900/30", text: "text-green-700 dark:text-green-400", icon: ShieldCheck };
    if (score >= 6) return { bg: "bg-yellow-100 dark:bg-yellow-900/30", text: "text-yellow-700 dark:text-yellow-400", icon: Shield };
    return { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400", icon: AlertCircle };
  };
  
  const trustStyle = getTrustColor(news.enhanced_trust_score);
  const TrustIcon = trustStyle.icon;

  return (
    <div className={cn(
        "bg-white dark:bg-slate-800 rounded-lg p-4 mb-4 shadow-md dark:shadow-sm border border-slate-200 dark:border-slate-700/50 transition-colors",
        isPro && getSentimentColor(news.sentiment_label)
    )}>
      {/* Header: Source & Time */}
      <div className="flex justify-between items-center mb-2 text-xs text-slate-500 dark:text-slate-400">
        <span className="bg-slate-100 dark:bg-slate-700/50 px-2 py-0.5 rounded text-[10px] uppercase font-medium tracking-wider">
          {news.topic_category || "News"}
        </span>
        <div className="flex items-center gap-2">
            {news.sentiment_label && isPro && getSentimentIcon(news.sentiment_label)}
            <span>{formatDistanceToNow(new Date(news.published_at), { addSuffix: true })}</span>
        </div>
      </div>

      {/* Title */}
      <h3 className="font-bold text-slate-900 dark:text-slate-100 text-[15px] leading-snug mb-2 line-clamp-2">
        {news.title}
      </h3>

      {/* Source Link & AI Quality */}
      <div className="flex items-center gap-2 mb-2">
        <Link
          href={`/news/${news.id}`}
          className="text-xs text-blue-500 dark:text-blue-400 hover:underline flex items-center gap-1"
        >
          {/* Enhanced Trust Badge */}
          {news.enhanced_trust_score && (
            <div
              className={cn(
                "text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 cursor-help",
                trustStyle.bg,
                trustStyle.text
              )}
              title={news.trust_breakdown ?
                `Base: ${news.trust_breakdown.base.toFixed(1)} | Smart Money: ${news.trust_breakdown.smart_money_bonus >= 0 ? '+' : ''}${news.trust_breakdown.smart_money_bonus.toFixed(2)} | Sentiment: ${news.trust_breakdown.sentiment_bonus >= 0 ? '+' : ''}${news.trust_breakdown.sentiment_bonus.toFixed(2)} | OnChain: +${news.trust_breakdown.onchain_bonus.toFixed(2)}`
                : undefined
              }
            >
              <TrustIcon className="w-3 h-3" />
              {t('card.trustLabel')}: {news.enhanced_trust_score.toFixed(1)}/10
            </div>
          )}
          <ExternalLink className="w-3 h-3" />
          {t('card.readMore')}
        </Link>
        <span className={cn("text-[10px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1", aiQuality.bg, aiQuality.color)}>
          <AIIcon className="w-3 h-3" />
          {aiQuality.label}
        </span>
      </div>

      {/* AI Summary Section */}
      <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700/50">
            {canViewContent ? (
          <div className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-light">
            {news.summary_vi || "AI Summary not available yet."}
          </div>
        ) : (
          <div className="text-center py-4">
            <Lock className="w-6 h-6 mx-auto mb-2 text-slate-400" />
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              {user ? t('card.unlockPrompt', { cost: 50, balance: user.balance.toFixed(2) }) : t('card.loginToUnlock')}
            </p>
            <button 
              onClick={(e) => {
                e.preventDefault();
                const event = new CustomEvent('openTokenModal', { detail: { newsId: news.id, action: 'unlock' } });
                window.dispatchEvent(event);
              }}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-full text-xs font-semibold transition-all"
            >
              {t('card.unlockButton', { cost: 50 })}
            </button>
          </div>
        )}
      </div>

      {/* Tags & Coins */}
      <div className="mt-3 flex flex-wrap gap-1.5">
          {/* Display Coins */}
          {news.coins_mentioned && Array.isArray(JSON.parse(JSON.stringify(news.coins_mentioned))) && 
            (JSON.parse(JSON.stringify(news.coins_mentioned)) as string[]).slice(0, 3).map((coin, idx) => (
               <span key={idx} className="text-[10px] font-bold text-orange-400 bg-orange-400/10 px-1.5 py-0.5 rounded">
                   ${coin}
               </span>
            ))
          }
          {/* Tags */}
          {tagsDisplay.slice(0, 2).map((tag, idx) => (
              <span key={`t-${idx}`} className="text-[10px] text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-1.5 py-0.5 rounded">
                  #{tag}
              </span>
          ))}
      </div>

      {/* Vote Actions */}
      <VoteActions newsId={news.id} />
    </div>
  );
};
