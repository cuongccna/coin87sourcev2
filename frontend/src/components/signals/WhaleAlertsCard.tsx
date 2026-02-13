'use client';

import { memo } from 'react';
import { useTranslations } from 'next-intl';
import { WhaleAlert } from '@/types/signals';

interface Props {
  data: WhaleAlert[];
}

function WhaleAlertsCard({ data }: Props) {
  const t = useTranslations('signals');
  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          🐋 {t('whaleAlerts.title')}
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center py-6 sm:py-8">
          {t('whaleAlerts.noAlerts')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
        🐋 {t('whaleAlerts.title')} ({data.length})
      </h2>

      <div className="space-y-3">
        {data.slice(0, 5).map((alert) => (
          <div
            key={alert.id}
            className={`p-4 rounded-lg border-l-4 ${
              alert.alert_type === 'ACCUMULATION'
                ? 'bg-green-50 dark:bg-green-900/20 border-green-500'
                : 'bg-red-50 dark:bg-red-900/20 border-red-500'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">
                  {alert.alert_type === 'ACCUMULATION' ? '🟢' : '🔴'}
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {alert.alert_type === 'ACCUMULATION' ? t('whaleAlerts.accumulation') : t('whaleAlerts.distribution')}
                </span>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {new Date(alert.created_at).toLocaleString('vi-VN')}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-3">
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{t('whaleAlerts.netFlow')}</div>
                <div className={`text-lg font-bold ${
                  alert.net_flow > 0
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}>
                  {alert.net_flow > 0 ? '+' : ''}{alert.net_flow.toFixed(2)}M
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{t('whaleAlerts.volume')}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  ${alert.volume.toFixed(1)}M
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{t('whaleAlerts.transactions')}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {alert.tx_count}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {data.length > 5 && (
        <div className="mt-4 text-center">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {t('whaleAlerts.moreAlerts', { count: data.length - 5 })}
          </span>
        </div>
      )}
    </div>
  );
}

export default memo(WhaleAlertsCard);
