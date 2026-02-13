'use client';

import { memo } from 'react';
import { useTranslations } from 'next-intl';
import { OnChainIntelligence } from '@/types/signals';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Props {
  data: OnChainIntelligence | null | undefined;
}

const stateColors = {
  ACCUMULATION: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  DISTRIBUTION: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  NEUTRAL: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  UNKNOWN: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
};

function OnChainCard({ data }: Props) {
  const t = useTranslations('signals');
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          ⛓️ {t('onchain.title')}
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center py-6 sm:py-8">
          {t('onchain.noData')}
        </p>
      </div>
    );
  }

  const chartData = [
    {
      name: t('onchain.netFlow'),
      value: data.whale_net_flow,
      fill: data.whale_net_flow > 0 ? '#10b981' : '#ef4444',
    },
    {
      name: t('onchain.dominance'),
      value: data.whale_dominance,
      fill: '#3b82f6',
    },
    {
      name: t('onchain.txCount'),
      value: data.whale_tx_count,
      fill: '#8b5cf6',
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          ⛓️ {t('onchain.title')}
        </h2>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${stateColors[data.state]}`}>
          {data.state}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 12 }} />
              <YAxis tick={{ fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Info Panel */}
        <div className="space-y-4">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('onchain.bias')}</div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">
                {data.bias === 'BULLISH' ? '📈' : data.bias === 'BEARISH' ? '📉' : '➡️'}
              </span>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {data.bias}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('onchain.score')}</div>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {data.score.toFixed(1)}/100
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('onchain.netFlow')}</div>
            <div className={`text-2xl font-bold ${
              data.whale_net_flow > 0
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}>
              {data.whale_net_flow > 0 ? '+' : ''}{data.whale_net_flow.toFixed(2)}M
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('onchain.dominance')}</div>
              <div className="text-lg font-bold text-gray-900 dark:text-white">
                {data.whale_dominance.toFixed(1)}%
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{t('onchain.txCount')}</div>
              <div className="text-lg font-bold text-gray-900 dark:text-white">
                {data.whale_tx_count}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(OnChainCard);
