"use client";

import React from "react";
import useSWRInfinite from "swr/infinite";
import { useInView } from "react-intersection-observer";
import { NewsCard } from "./NewsCard";
import { NewsItem } from "@/types";
import { Loader2 } from "lucide-react";

// The fetcher function for SWR
const fetcher = (url: string) => fetch(url).then((res) => res.json());

// API Base URL (Should be environmental variable in production)
const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/news/` : "http://localhost:9010/api/v1/news/"; 

export const NewsFeed = () => {
    const [filterTag, setFilterTag] = React.useState<string | null>(null)

    // Listen to trending filter events
    React.useEffect(() => {
        const handleFilter = (e: CustomEvent) => {
            console.log('Filter by narrative:', e.detail)
            setFilterTag(e.detail)
        }
        window.addEventListener('filterByNarrative' as any, handleFilter)
        return () => window.removeEventListener('filterByNarrative' as any, handleFilter)
    }, [])

    // 1. Setup SWR Infinite
    const getKey = (pageIndex: number, previousPageData: NewsItem[]) => {
        if (previousPageData && !previousPageData.length) return null; // reached the end
        // API skip logic: pageIndex * limit (e.g. 10)
        // Assume limit is 10 for pagination testing, 20/50 normally
        const limit = 10; 
        return `${API_URL}?skip=${pageIndex * limit}&limit=${limit}`; 
    };

    const { data, size, setSize, isLoading, isValidating, mutate } = useSWRInfinite<NewsItem[]>(getKey, fetcher, {
        revalidateFirstPage: false,
        revalidateOnFocus: false, // Save resources
        dedupingInterval: 10000 // Prevent duplicate requests within 10s
    });

    // Auto refresh news every 60 seconds
    React.useEffect(() => {
        const interval = setInterval(() => {
            console.log('Auto refreshing news...')
            mutate()
        }, 60000)
        return () => clearInterval(interval)
    }, [mutate])

    // 2. Setup Infinite Scroll Trigger
    const { ref, inView } = useInView();

    React.useEffect(() => {
        if (inView && !isValidating) {
            setSize(size + 1);
        }
    }, [inView, isValidating, setSize, size]);

    // Flatten logic and deduplicate by `id` to avoid duplicate React keys when
    // paginating (backend may return overlapping pages).
    const flattened = data ? ([] as NewsItem[]).concat(...data) : [];
    const seen = new Set<string | number>();
    let news = flattened.filter((item) => {
        const key = item.id ?? `${item.title ?? ''}-${item.published_at ?? ''}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    // Filter out news without AI summary
    news = news.filter(item => {
        return item.summary_vi && item.summary_vi !== "AI Summary not available yet."
    })

    // Apply trending filter
    if (filterTag) {
        news = news.filter(item => {
            const tags = item.tags ? (typeof item.tags === 'string' ? JSON.parse(item.tags) : item.tags) : [];
            return tags.includes(filterTag)
        })
    }
    const isEmpty = data?.[0]?.length === 0;
    const isReachingEnd = isEmpty || (data && data[data.length - 1]?.length < 10);

    return (
        <div className="max-w-md mx-auto px-4 pb-20 pt-4"> 
            {/* Feed Items */}
            {news.map((item, idx) => (
                <NewsCard key={`${item.id}-${item.published_at ?? idx}`} news={item} />
            ))}
            
            {/* Loading State Skeleton / Spinner */}
            <div className="py-4 text-center">
                {isLoading || isValidating ? (
                    <div className="flex flex-col items-center gap-2">
                         {/* Skeleton Effect - Pulsating Blocks */}
                         {news.length === 0 && Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="w-full bg-slate-800 h-40 rounded-lg animate-pulse mb-4 border border-slate-700/50" />
                         ))}
                         {news.length > 0 && <Loader2 className="w-6 h-6 text-slate-500 animate-spin" />}
                    </div>
                ) : null}

                {isReachingEnd && news.length > 0 && (
                    <p className="text-slate-500 text-xs mt-4">✓ You're all caught up</p>
                )}
            </div>

            {/* Invisible Trigger for Infinite Scroll */}
            {!isReachingEnd && <div ref={ref} className="h-4" />}
        </div>
    );
};
