'use client';

import { memo } from 'react';
import { useTranslations } from 'next-intl';
import { SmartMoneySignal } from '@/types/signals';

interface Props {
  coin: string;
  data: SmartMoneySignal | null | undefined;
}

const bandColors = {
  STRONG_BUY: 'bg-green-600 text-white',
  BUY: 'bg-green-500 text-white',
  ACCUMULATE: 'bg-green-400 text-gray-900',
  NEUTRAL: 'bg-gray-400 text-white',
  SELL: 'bg-red-400 text-white',
  STRONG_SELL: 'bg-red-600 text-white',
};

const directionIcons = {
  BULLISH: '📈',
  BEARISH: '📉',
  NEUTRAL: '➡️',
};

function SmartMoneyCard({ coin, data }: Props) {
  const t = useTranslations('signals');
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          💰 {t('smartMoney.title', { coin })}
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center py-6 sm:py-8">
          Chưa có dữ liệu Smart Money cho {coin}
        </p>
      </div>
    );
  }

  const scorePercentage = (data.score / 100) * 100;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3 sm:mb-4">
        <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
          💰 {t('smartMoney.title', { coin })}
        </h2>
        <span className="text-xl sm:text-2xl">
          {directionIcons[data.direction]}
        </span>
      </div>

      {/* Score Circle - Smaller on mobile */}
      <div className="flex justify-center mb-4 sm:mb-6">
        <div className="relative w-24 h-24 sm:w-32 sm:h-32">
          <svg className="transform -rotate-90 w-24 h-24 sm:w-32 sm:h-32">
            <circle
              cx="48"
              cy="48"
              r="42"
              stroke="currentColor"
              strokeWidth="6"
              fill="transparent"
              className="text-gray-200 dark:text-gray-700 sm:hidden"
            />
            <circle
              cx="48"
              cy="48"
              r="42"
              stroke="currentColor"
              strokeWidth="6"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 42}`}
              strokeDashoffset={`${2 * Math.PI * 42 * (1 - scorePercentage / 100)}`}
              className={`sm:hidden ${
                data.direction === 'BULLISH'
                  ? 'text-green-500'
                  : data.direction === 'BEARISH'
                  ? 'text-red-500'
                  : 'text-gray-500'
              }`}
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-gray-200 dark:text-gray-700 hidden sm:block"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={`${2 * Math.PI * 56}`}
              strokeDashoffset={`${2 * Math.PI * 56 * (1 - scorePercentage / 100)}`}
              className={`hidden sm:block ${
                data.direction === 'BULLISH'
                  ? 'text-green-500'
                  : data.direction === 'BEARISH'
                  ? 'text-red-500'
                  : 'text-gray-500'
              }`}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              {data.score}
            </span>
          </div>
        </div>
      </div>

      {/* Signal Band */}
      <div className="mb-3 sm:mb-4">
        <span className={`block w-full text-center py-2 rounded-lg text-xs sm:text-sm font-semibold ${bandColors[data.band]}`}>
          {data.band.replace('_', ' ')}
        </span>
      </div>

      {/* Details */}
      <div className="space-y-2 sm:space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{t('smartMoney.confidence')}</span>
          <span className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
            {(data.confidence * 100).toFixed(0)}%
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{t('smartMoney.timeframe')}</span>
          <span className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
            {data.timeframe}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">{t('smartMoney.modules')}</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.modules_active}/12
          </span>
        </div>
      </div>

      {/* Description */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-sm text-gray-700 dark:text-gray-300">
          {data.description_vi}
        </p>
      </div>
    </div>
  );
}

export default memo(SmartMoneyCard);
