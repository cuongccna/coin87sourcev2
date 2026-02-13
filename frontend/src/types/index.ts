// Mock types for now, will sync with backend schema later

export interface TrustBreakdown {
  base: number;
  smart_money_bonus: number;
  sentiment_bonus: number;
  onchain_bonus: number;
}

export interface NewsItem {
  id: number;
  title: string;
  source_id: number; // In real app, might want source name/icon
  url: string;
  published_at: string;
  tags: string[];
  topic_category?: string;
  image_url?: string;
  
  // Content fields
  content?: string;  // Short content/description
  raw_content?: string;  // Full article content
  
  // AI Fields
  summary_vi?: string;
  sentiment_score?: number;
  sentiment_label?: string;
  coins_mentioned?: string[]; // JSON string or array depending on backend
  risk_level?: string;
  
  // Enhanced Trust Score (from trading signals)
  enhanced_trust_score?: number;
  trust_breakdown?: TrustBreakdown;
}

export type UserTier = 'Free' | 'Pro' | 'Elite';

export interface User {
  id: string;
  email: string;
  created_at?: string;
  tier: UserTier;
  balance: number;
}
