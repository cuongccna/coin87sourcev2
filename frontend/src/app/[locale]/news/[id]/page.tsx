"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { NewsItem } from "@/types";
import { ArrowLeft, ExternalLink, TrendingUp, TrendingDown, Minus, CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { VoteActions } from "@/components/VoteActions";
import toast from "react-hot-toast";

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [news, setNews] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010'}/api/v1/news/${params.id}`);
        if (res.ok) {
          const data = await res.json();
          setNews(data);
        } else {
          toast.error("News not found");
          router.push("/");
        }
      } catch (error) {
        console.error("Failed to fetch news:", error);
        toast.error("Failed to load news");
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchNews();
    }
  }, [params.id, router]);

  const getAIQuality = (summaryVi?: string) => {
    if (!summaryVi || summaryVi === "AI Summary not available yet.") {
      return { label: "No AI", icon: XCircle, color: "text-red-500", bg: "bg-red-500/10" };
    }
    const len = summaryVi.length;
    if (len > 200) return { label: "Complete", icon: CheckCircle2, color: "text-green-500", bg: "bg-green-500/10" };
    if (len > 100) return { label: "Partial", icon: AlertCircle, color: "text-yellow-500", bg: "bg-yellow-500/10" };
    return { label: "Limited", icon: AlertCircle, color: "text-orange-500", bg: "bg-orange-500/10" };
  };

  const getSentimentIcon = (label?: string) => {
    switch (label) {
      case "Bullish": return <TrendingUp className="w-5 h-5 text-green-500" />;
      case "Bearish": return <TrendingDown className="w-5 h-5 text-red-500" />;
      default: return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!news) {
    return null;
  }

  const locale = Array.isArray(params.locale) ? params.locale[0] : params.locale;
  const summary = (locale === 'en' && news.summary_en ? news.summary_en : news.summary_vi) || news.summary_vi;

  const aiQuality = getAIQuality(summary);
  let tagsDisplay: string[] = [];
  if (Array.isArray(news.tags)) {
    tagsDisplay = news.tags;
  } else if (typeof news.tags === "string") {
    try {
      tagsDisplay = JSON.parse(news.tags);
    } catch (e) {}
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
        >
          <ArrowLeft size={20} />
          <span className="font-medium">Back</span>
        </button>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Meta */}
        <div className="flex items-center gap-3 mb-4 text-sm text-slate-500 dark:text-slate-400">
          <span className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs uppercase font-medium">
            {news.topic_category || "News"}
          </span>
          {news.sentiment_label && getSentimentIcon(news.sentiment_label)}
          <span>{formatDistanceToNow(new Date(news.published_at), { addSuffix: true })}</span>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4 leading-tight">
          {news.title}
        </h1>

        {/* AI Quality & External Link */}
        <div className="flex items-center gap-3 mb-6">
          <span className={cn("text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1.5", aiQuality.bg, aiQuality.color)}>
            <aiQuality.icon className="w-4 h-4" />
            {aiQuality.label}
          </span>
          <a
            href={news.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-500 dark:text-blue-400 hover:underline flex items-center gap-1"
          >
            <ExternalLink className="w-4 h-4" />
            Original Source
          </a>
        </div>

        {/* AI Summary */}
        <div className="bg-white dark:bg-slate-900 rounded-xl p-6 mb-6 border border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
            <span className="w-1 h-6 bg-blue-500 rounded-full"></span>
            AI Analysis
          </h2>
          <div className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
            {summary || "AI Summary not available yet."}
          </div>
        </div>

        {/* Full Article */}
        {news.raw_content && (
          <div className="bg-white dark:bg-slate-900 rounded-xl p-6 mb-6 border border-slate-200 dark:border-slate-800">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
              <span className="w-1 h-6 bg-green-500 rounded-full"></span>
              Full Article
            </h2>
            <div className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {news.raw_content}
            </div>
          </div>
        )}

        {/* Tags & Coins */}
        <div className="flex flex-wrap gap-2 mb-6">
          {news.coins_mentioned && Array.isArray(JSON.parse(JSON.stringify(news.coins_mentioned))) &&
            (JSON.parse(JSON.stringify(news.coins_mentioned)) as string[]).map((coin, idx) => (
              <span key={idx} className="text-sm font-bold text-orange-500 bg-orange-500/10 px-3 py-1 rounded-full">
                ${coin}
              </span>
            ))
          }
          {tagsDisplay.map((tag, idx) => (
            <span key={`t-${idx}`} className="text-sm text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-3 py-1 rounded-full">
              #{tag}
            </span>
          ))}
        </div>

        {/* Vote Actions */}
        <VoteActions newsId={news.id} />
      </div>
    </div>
  );
}
