"use client";

import { memo } from 'react';
import { useTranslations } from 'next-intl';
import { SentimentReport } from '@/types/signals';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Props {
  coin: string;
  data: SentimentReport | null | undefined;
}

const COLORS = {
  bullish: '#10b981',
  bearish: '#ef4444',
  neutral: '#6b7280',
};

function SentimentCard({ coin, data }: Props) {
  const t = useTranslations('signals');
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          📊 {t('sentiment.title', { coin })}
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center py-6 sm:py-8">
          {t('sentiment.noData')}
        </p>
      </div>
    );
  }

  const chartData = [
    { name: t('sentiment.bullish'), value: data.bullish_count, fill: COLORS.bullish },
    { name: t('sentiment.bearish'), value: data.bearish_count, fill: COLORS.bearish },
    { name: t('sentiment.neutral'), value: data.neutral_count, fill: COLORS.neutral },
  ];

  const total = data.bullish_count + data.bearish_count + data.neutral_count;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">
          😊 Sentiment: {coin}
        </h2>
        <span className={`text-2xl ${
          data.signal === 'BULLISH' ? '📈' : data.signal === 'BEARISH' ? '📉' : '➡️'
        }`}>
          {data.signal === 'BULLISH' ? '📈' : data.signal === 'BEARISH' ? '📉' : '➡️'}
        </span>
      </div>

      {/* Pie Chart */}
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={70}
              paddingAngle={2}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center">
          <div className="text-xs text-green-700 dark:text-green-300 mb-1">{t('sentiment.bullish')}</div>
          <div className="text-lg font-bold text-green-900 dark:text-green-100">
            {data.bullish_count}
          </div>
          <div className="text-xs text-green-600 dark:text-green-400">
            {((data.bullish_count / total) * 100).toFixed(0)}%
          </div>
        </div>

        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 text-center">
          <div className="text-xs text-red-700 dark:text-red-300 mb-1">{t('sentiment.bearish')}</div>
          <div className="text-lg font-bold text-red-900 dark:text-red-100">
            {data.bearish_count}
          </div>
          <div className="text-xs text-red-600 dark:text-red-400">
            {((data.bearish_count / total) * 100).toFixed(0)}%
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('sentiment.neutral')}</div>
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {data.neutral_count}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {((data.neutral_count / total) * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">{t('sentiment.avgScore')}</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.average_score.toFixed(2)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">{t('sentiment.weighted')}</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.weighted_sentiment.toFixed(2)}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600 dark:text-gray-400">{t('sentiment.velocity')}</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.velocity.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Sources */}
      {data.sources && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">{t('sentiment.sources')}</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.sources).map(([source, count]) => (
              <span
                key={source}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
              >
                {source}: {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default memo(SentimentCard);
