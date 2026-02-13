"use client";

import { Link } from "@/i18n/navigation";
import { useTranslations } from 'next-intl';
import { NewsFeed } from "@/components/NewsFeed";
import { Header } from "@/components/Header";
import { TrendingBar } from "@/components/TrendingBar";
import { InstallPWA } from "@/components/InstallPWA";
import { OfflineIndicator } from "@/components/OfflineIndicator";

export default function Home() {
  const t = useTranslations('home');
  
  return (
    <div className="min-h-screen pb-20 bg-slate-50 dark:bg-slate-900 transition-colors">
      <Header />
      <OfflineIndicator />
      <TrendingBar />
      
      {/* Trading Signals Quick Access */}
      <div className="container mx-auto px-4 max-w-2xl mt-4 mb-6">
        <Link 
          href="/signals"
          className="block bg-linear-to-r from-blue-500 to-purple-600 dark:from-blue-600 dark:to-purple-700 rounded-lg p-4 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
        >
          <div className="flex items-center justify-between text-white">
            <div>
              <h3 className="text-lg font-bold mb-1">{t('signalsCard.title')}</h3>
              <p className="text-sm text-blue-100">
                {t('signalsCard.subtitle')}
              </p>
            </div>
            <svg 
              className="w-6 h-6" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </Link>
      </div>
      
      <main className="container mx-auto px-4 max-w-2xl">
        <NewsFeed />
      </main>
      <InstallPWA />
    </div>
  );
}
