'use client';

import { useState, useEffect, useRef } from 'react';
import { Link } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import toast from 'react-hot-toast';
import { SignalsDashboard } from '@/types/signals';
import TradingDecisionCard from '@/components/signals/TradingDecisionCard';
import SmartMoneyCard from '@/components/signals/SmartMoneyCard';
import SentimentCard from '@/components/signals/SentimentCard';
import OnChainCard from '@/components/signals/OnChainCard';
import WhaleAlertsCard from '@/components/signals/WhaleAlertsCard';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function SignalsPage() {
  const t = useTranslations('signals');
  const tCommon = useTranslations('common');
  const prevDataRef = useRef<SignalsDashboard | null>(null);
  const { data, error, isLoading, mutate, isValidating } = useSWR<SignalsDashboard>(
    `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:9010'}/api/v1/signals/dashboard`,
    fetcher,
    {
      refreshInterval: 30000, // Auto-refresh every 30s
      revalidateOnFocus: false,
      dedupingInterval: 10000,
    }
  );

  // Detect new signals and show toast notifications
  useEffect(() => {
    if (!data || !prevDataRef.current) {
      prevDataRef.current = data || null;
      return;
    }

    const prev = prevDataRef.current;
    const curr = data;

    // Check for new whale alerts
    if (curr.whale_alerts && prev.whale_alerts) {
      const newAlerts = curr.whale_alerts.filter(
        (alert) => !prev.whale_alerts?.some((p) => p.id === alert.id)
      );
      if (newAlerts.length > 0) {
        const message = newAlerts.length === 1 
          ? t('whaleAlerts.newAlert', { count: newAlerts.length })
          : t('whaleAlerts.newAlerts', { count: newAlerts.length });
        toast.success(message, {
          duration: 5000,
          position: 'top-right',
        });
      }
    }

    // Check for risk band changes
    if (curr.trading_decision?.risk_band !== prev.trading_decision?.risk_band) {
      const riskColor = curr.trading_decision?.risk_band === 'EXTREME' ? '🔴' : 
                       curr.trading_decision?.risk_band === 'HIGH' ? '🟠' : '🟢';
      toast(`${riskColor} ${t('notifications.riskChange', { risk: curr.trading_decision?.risk_band })}`, {
        duration: 4000,
        position: 'top-right',
      });
    }

    prevDataRef.current = data;
  }, [data]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
            {t('loadError')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {t('cannotConnect')}
          </p>
          <button
            onClick={() => mutate()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {tCommon('retry')}
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">{tCommon('loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-8 px-3 sm:px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-4 sm:mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link href="/" className="inline-flex items-center px-3 py-1.5 bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-200">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 011.414 1.414L6.414 9H17a1 1 0 110 2H6.414l3.293 3.293a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
              <span className="ml-2 hidden sm:inline">{tCommon('back')}</span>
            </Link>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">
                {t('title')}
              </h1>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">
                {t('subtitle')}
              </p>
            </div>
          </div>
          {isValidating && (
            <div className="flex items-center gap-2 text-xs sm:text-sm text-blue-600 dark:text-blue-400">
              <div className="h-3 w-3 sm:h-4 sm:w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
              <span>{t('updating')}</span>
            </div>
          )}
        </div>

        {/* Grid Layout - Mobile Optimized */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 md:gap-6">
          {/* Trading Decision (Full width on all screens) */}
          <div className="md:col-span-2">
            <TradingDecisionCard data={data?.trading_decision} />
          </div>

          {/* Smart Money Signals - Stack on mobile, side-by-side on tablet+ */}
          <SmartMoneyCard coin="BTC" data={data?.smart_money_btc} />
          <SmartMoneyCard coin="ETH" data={data?.smart_money_eth} />

          {/* Sentiment Reports */}
          <SentimentCard coin="BTC" data={data?.sentiment_btc} />
          <SentimentCard coin="ETH" data={data?.sentiment_eth} />

          {/* OnChain Intelligence */}
          <div className="md:col-span-2">
            <OnChainCard data={data?.onchain} />
          </div>

          {/* Whale Alerts */}
          <div className="md:col-span-2">
            <WhaleAlertsCard data={data?.whale_alerts || []} />
          </div>
        </div>

        {/* Last Update */}
        <div className="mt-4 sm:mt-6 text-center text-xs sm:text-sm text-gray-500 dark:text-gray-400">
          {t('lastUpdate')}: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
