'use client';

import { memo } from 'react';
import { useTranslations } from 'next-intl';
import { TradingDecision } from '@/types/signals';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface Props {
  data: TradingDecision | null | undefined;
}

const riskBandColors = {
  SAFE: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  LOW: 'bg-green-50 text-green-700 dark:bg-green-800 dark:text-green-100',
  MODERATE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  HIGH: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  EXTREME: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
};

function TradingDecisionCard({ data }: Props) {
  const t = useTranslations('signals');
  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          🎯 {t('tradingDecision.title')}
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          Chưa có dữ liệu quyết định giao dịch
        </p>
      </div>
    );
  }

  // Transform risk components for radar chart (localized subjects)
  const chartData = [
    { subject: t('chart.marketVol'), value: data.risk_components.market_volatility },
    { subject: t('chart.liquidity'), value: data.risk_components.liquidity },
    { subject: t('chart.sentiment'), value: data.risk_components.news_sentiment },
    { subject: t('chart.technical'), value: data.risk_components.technical_indicators },
    { subject: t('chart.volume'), value: data.risk_components.volume_analysis },
    { subject: t('chart.whale'), value: data.risk_components.whale_activity },
    { subject: t('chart.correlation'), value: data.risk_components.correlation_risk },
    { subject: t('chart.regulatory'), value: data.risk_components.regulatory_risk },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg sm:rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
          🎯 {t('tradingDecision.title')}
        </h2>
        <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-semibold ${riskBandColors[data.risk_band]}`}>
          {(() => {
            const raw = String(data.risk_band || '');
            const key = raw.toLowerCase() === 'moderate' ? 'medium' : raw.toLowerCase();
            const localized = t(`tradingDecision.riskBand.${key}`);
            return localized || raw;
          })()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        {/* Radar Chart - Smaller on mobile */}
        <div className="h-64 sm:h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={chartData}>
              <PolarGrid stroke="#9ca3af" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 10 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} />
              <Radar
                name="Risk Score"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.5}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Info Panel */}
        <div className="space-y-3 sm:space-y-4">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 sm:p-4">
            <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-1">{t('tradingDecision.risk')}</div>
            <div className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              {data.overall_risk.toFixed(1)}/100
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('tradingDecision.confidence')}</div>
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {(data.confidence * 100).toFixed(0)}%
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('tradingDecision.action')}</div>
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {(() => {
                  const code = String(data.bot_action || '').toLowerCase();
                  const mapped = t(`tradingDecision.actions.${code}`);
                  return mapped || data.bot_action;
                })()}
              </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('maxPosition')}</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {data.max_position_pct}%
            </div>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      {data.active_alerts && data.active_alerts.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            🚨 {t('activeAlerts')}
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.active_alerts.map((alert, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-xs"
              >
                {(() => {
                  const text = String(alert || '');
                  if (/whale/i.test(text)) return t('alerts.highWhale');
                  const m = text.match(/Volume spike on (\w+)/i);
                  if (m) return t('alerts.volumeSpikeOn', { coin: m[1] });
                  return text;
                })()}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action Recommendation */}
      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
          💡 {(() => {
            const act = String(data.action || '');
            const parts = act.split(' - ');
            const code = parts[0]?.toLowerCase();
            const mapped = t(`tradingDecision.actions.${code}`);
            return (mapped || parts[0]) + (parts[1] ? ` - ${parts.slice(1).join(' - ')}` : '');
          })()}
        </p>
      </div>
    </div>
  );
}

export default memo(TradingDecisionCard);
