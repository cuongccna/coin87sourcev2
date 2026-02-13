// Trading Signals Types

export type RiskBand = 'SAFE' | 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';
export type SignalDirection = 'BULLISH' | 'BEARISH' | 'NEUTRAL';
export type SignalBand = 'STRONG_BUY' | 'BUY' | 'ACCUMULATE' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL';
export type OnChainState = 'ACCUMULATION' | 'DISTRIBUTION' | 'NEUTRAL' | 'UNKNOWN';
export type OnChainBias = 'BULLISH' | 'BEARISH' | 'NEUTRAL';

export interface RiskComponents {
  market_volatility: number;
  liquidity: number;
  news_sentiment: number;
  technical_indicators: number;
  volume_analysis: number;
  whale_activity: number;
  correlation_risk: number;
  regulatory_risk: number;
}

export interface TradingDecision {
  id: number;
  overall_risk: number;
  risk_band: RiskBand;
  confidence: number;
  action: string;
  risk_components: RiskComponents;
  active_alerts: string[];
  bot_action: string;
  max_position_pct: number;
  created_at: string;
}

export interface SmartMoneySignal {
  id: number;
  coin: string;
  score: number;
  band: SignalBand;
  direction: SignalDirection;
  confidence: number;
  timeframe: string;
  modules_active: number;
  description_vi: string;
  created_at: string;
}

export interface SentimentSources {
  twitter?: number;
  reddit?: number;
  news?: number;
  telegram?: number;
}

export interface SentimentReport {
  id: number;
  coin: string;
  signal: SignalDirection;
  bullish_count: number;
  bearish_count: number;
  neutral_count: number;
  average_score: number;
  weighted_sentiment: number;
  velocity: number;
  sources: SentimentSources;
  created_at: string;
}

export interface OnChainIntelligence {
  id: number;
  state: OnChainState;
  bias: OnChainBias;
  score: number;
  whale_net_flow: number;
  whale_dominance: number;
  whale_tx_count: number;
  created_at: string;
}

export interface WhaleAlert {
  id: number;
  alert_type: 'ACCUMULATION' | 'DISTRIBUTION';
  net_flow: number;
  volume: number;
  tx_count: number;
  created_at: string;
}

export interface SignalsDashboard {
  trading_decision: TradingDecision | null;
  smart_money_btc: SmartMoneySignal | null;
  smart_money_eth: SmartMoneySignal | null;
  sentiment_btc: SentimentReport | null;
  sentiment_eth: SentimentReport | null;
  onchain: OnChainIntelligence | null;
  whale_alerts: WhaleAlert[];
}
