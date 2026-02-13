# GIẢI PHÁP TÍCH HỢP TRADING SIGNALS VÀO NEWS TRUST SCORE

## 📊 TỔNG QUAN

Kết hợp các chỉ số trading signals (On-Chain, Smart Money, Sentiment) vào trust score của tin tức để tạo ra một hệ thống đánh giá tin cậy thông minh hơn, dựa trên dữ liệu thị trường thực tế.

---

## 🔗 KIẾN TRÚC LIÊN KẾT

### 1. Cơ chế Timestamp Correlation

```python
# Matching Logic: News article vs Trading Signals
# Chỉ lấy signals trong khoảng thời gian hợp lý

def get_relevant_signals(news_published_at: datetime) -> SignalsContext:
    """
    Lấy signals gần nhất với thời điểm xuất bản tin
    Window: ±2 giờ từ thời điểm published_at
    """
    time_window_start = news_published_at - timedelta(hours=2)
    time_window_end = news_published_at + timedelta(hours=2)
    
    # Query signals trong time window
    signals = await db.query(
        select(TradingSignals)
        .where(
            TradingSignals.timestamp >= time_window_start,
            TradingSignals.timestamp <= time_window_end
        )
        .order_by(TradingSignals.timestamp.desc())
        .limit(1)
    )
    
    return signals
```

---

## 🧮 CÔNG THỨC TÍNH ENHANCED TRUST SCORE

### Current Trust Score (Baseline)
```python
# Hiện tại (từ Source.trust_score)
base_trust = source.trust_score  # 0-10
```

### New Enhanced Trust Score
```python
def calculate_enhanced_trust(
    base_trust: float,
    smart_money_score: float,  # 0-100
    sentiment: Dict,
    onchain_confidence: float,  # 0-1
    news_sentiment_keywords: List[str]
) -> float:
    """
    Trust Score = Base Trust + Signal Bonus + Sentiment Alignment
    Max: 10.0
    """
    
    # 1. Smart Money Adjustment (-0.5 to +0.5)
    # Nếu Smart Money bullish mạnh → tin về "tăng giá" được boost
    # Nếu Smart Money bearish mạnh → tin về "giảm giá" được boost
    smart_money_bonus = 0.0
    if smart_money_score >= 70:  # Strong bullish
        if any(keyword in news_sentiment_keywords for keyword in ["rally", "surge", "bullish", "tăng"]):
            smart_money_bonus = +0.5
        elif any(keyword in news_sentiment_keywords for keyword in ["crash", "dump", "bearish", "giảm"]):
            smart_money_bonus = -0.3  # Tin trái chiều → giảm trust
    elif smart_money_score <= 30:  # Strong bearish
        if any(keyword in news_sentiment_keywords for keyword in ["crash", "dump", "bearish", "giảm"]):
            smart_money_bonus = +0.5
        elif any(keyword in news_sentiment_keywords for keyword in ["rally", "surge", "bullish", "tăng"]):
            smart_money_bonus = -0.3
    
    # 2. Sentiment Alignment (-0.3 to +0.3)
    # So sánh sentiment của tin với sentiment thị trường
    market_bullish_ratio = sentiment['bullish_count'] / sentiment['total_messages']
    sentiment_bonus = 0.0
    
    if market_bullish_ratio > 0.6:  # Thị trường rất bullish
        if any(keyword in news_sentiment_keywords for keyword in ["bullish", "tăng", "rally"]):
            sentiment_bonus = +0.3
        else:
            sentiment_bonus = -0.2
    elif market_bullish_ratio < 0.4:  # Thị trường bearish
        if any(keyword in news_sentiment_keywords for keyword in ["bearish", "giảm", "crash"]):
            sentiment_bonus = +0.3
        else:
            sentiment_bonus = -0.2
    
    # 3. OnChain Confidence Boost (0 to +0.2)
    # OnChain data càng tốt → tin càng tin cậy
    onchain_bonus = onchain_confidence * 0.2
    
    # Tính tổng
    enhanced_trust = base_trust + smart_money_bonus + sentiment_bonus + onchain_bonus
    
    # Clamp về [0, 10]
    return max(0.0, min(10.0, enhanced_trust))
```

---

## 📝 DATABASE SCHEMA EXTENSION

### Thêm bảng liên kết News ↔ Signals

```sql
CREATE TABLE news_signal_correlation (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id) ON DELETE CASCADE,
    
    -- Signals tại thời điểm gần nhất với news
    smart_money_signal_id INTEGER REFERENCES smart_money_signals(id),
    sentiment_report_id INTEGER REFERENCES sentiment_reports(id),
    onchain_intelligence_id INTEGER REFERENCES onchain_intelligence(id),
    
    -- Cached enhanced trust score
    enhanced_trust_score FLOAT NOT NULL,
    base_trust_score FLOAT NOT NULL,
    smart_money_bonus FLOAT DEFAULT 0.0,
    sentiment_bonus FLOAT DEFAULT 0.0,
    onchain_bonus FLOAT DEFAULT 0.0,
    
    -- Metadata
    time_diff_seconds INTEGER,  -- Khoảng cách thời gian giữa news và signals
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(news_id)  -- Mỗi tin chỉ có 1 correlation
);

CREATE INDEX idx_news_signal_correlation_news ON news_signal_correlation(news_id);
CREATE INDEX idx_news_signal_correlation_enhanced_trust ON news_signal_correlation(enhanced_trust_score DESC);
```

---

## 🔄 WORKFLOW TÍCH HỢP

### 1. Khi Crawl Tin Mới

```python
async def process_new_article(article_data: dict, db: AsyncSession):
    # 1. Lưu tin vào DB như cũ
    news = News(**article_data)
    db.add(news)
    await db.flush()
    
    # 2. Tìm signals gần nhất theo thời gian
    signals_context = await get_relevant_signals(news.published_at, db)
    
    # 3. Tính enhanced trust score
    if signals_context:
        enhanced_trust = calculate_enhanced_trust(
            base_trust=news.source.trust_score,
            smart_money_score=signals_context.smart_money.score,
            sentiment=signals_context.sentiment,
            onchain_confidence=signals_context.onchain.confidence,
            news_sentiment_keywords=extract_keywords(news.title, news.content)
        )
        
        # 4. Lưu correlation
        correlation = NewsSignalCorrelation(
            news_id=news.id,
            smart_money_signal_id=signals_context.smart_money.id,
            sentiment_report_id=signals_context.sentiment.id,
            onchain_intelligence_id=signals_context.onchain.id,
            enhanced_trust_score=enhanced_trust,
            base_trust_score=news.source.trust_score,
            time_diff_seconds=int((signals_context.timestamp - news.published_at).total_seconds())
        )
        db.add(correlation)
    
    await db.commit()
```

### 2. API Endpoint Trả Về Enhanced Trust

```python
@router.get("/news", response_model=List[NewsResponse])
async def get_news(db: AsyncSession):
    """
    Trả về news với enhanced_trust_score
    """
    query = (
        select(
            News,
            NewsSignalCorrelation.enhanced_trust_score,
            NewsSignalCorrelation.smart_money_bonus,
            NewsSignalCorrelation.sentiment_bonus,
            NewsSignalCorrelation.onchain_bonus
        )
        .outerjoin(NewsSignalCorrelation, News.id == NewsSignalCorrelation.news_id)
        .order_by(NewsSignalCorrelation.enhanced_trust_score.desc().nulls_last())
    )
    
    result = await db.execute(query)
    news_list = []
    
    for row in result:
        news_dict = {
            **row.News.__dict__,
            "enhanced_trust_score": row.enhanced_trust_score,
            "trust_breakdown": {
                "base": row.News.source.trust_score,
                "smart_money_bonus": row.smart_money_bonus,
                "sentiment_bonus": row.sentiment_bonus,
                "onchain_bonus": row.onchain_bonus
            }
        }
        news_list.append(news_dict)
    
    return news_list
```

---

## 🎯 LOGIC CHI TIẾT

### A. Sentiment Keyword Extraction

```python
def extract_keywords(title: str, content: str) -> List[str]:
    """
    Trích xuất keywords sentiment từ tin
    """
    bullish_keywords = [
        "rally", "surge", "bullish", "gain", "rise", "pump",
        "tăng", "tích cực", "lạc quan", "bứt phá"
    ]
    bearish_keywords = [
        "crash", "dump", "bearish", "fall", "drop", "decline",
        "giảm", "sụt giảm", "bi quan", "rớt"
    ]
    
    text = (title + " " + content).lower()
    keywords = []
    
    for keyword in bullish_keywords:
        if keyword in text:
            keywords.append(keyword)
    
    for keyword in bearish_keywords:
        if keyword in text:
            keywords.append(keyword)
    
    return keywords
```

### B. Time Window Validation

```python
def is_signals_relevant(
    news_time: datetime, 
    signal_time: datetime,
    max_hours: int = 2
) -> bool:
    """
    Kiểm tra signals có hợp lý với thời gian tin không
    
    VD: Tin xuất bản lúc 10:00
    - Signals lúc 08:30 → OK (1.5h trước)
    - Signals lúc 11:30 → OK (1.5h sau)
    - Signals lúc 06:00 → KHÔNG (4h trước, quá xa)
    """
    time_diff = abs((signal_time - news_time).total_seconds() / 3600)
    return time_diff <= max_hours
```

---

## 📊 FRONTEND DISPLAY

### News Card với Enhanced Trust

```tsx
interface NewsWithTrust {
  title: string;
  enhanced_trust_score: number;
  trust_breakdown: {
    base: number;
    smart_money_bonus: number;
    sentiment_bonus: number;
    onchain_bonus: number;
  };
}

function NewsCard({ news }: { news: NewsWithTrust }) {
  const getTrustColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="border rounded-lg p-4">
      <h3>{news.title}</h3>
      
      {/* Enhanced Trust Score */}
      <div className="mt-2 flex items-center gap-2">
        <span className={`font-bold ${getTrustColor(news.enhanced_trust_score)}`}>
          Trust: {news.enhanced_trust_score.toFixed(1)}/10
        </span>
        
        {/* Tooltip hiển thị breakdown */}
        <div className="text-xs text-gray-500">
          (Base: {news.trust_breakdown.base}
          {news.trust_breakdown.smart_money_bonus > 0 && 
            ` +${news.trust_breakdown.smart_money_bonus.toFixed(1)} Smart Money`}
          {news.trust_breakdown.sentiment_bonus > 0 && 
            ` +${news.trust_breakdown.sentiment_bonus.toFixed(1)} Sentiment`}
          {news.trust_breakdown.onchain_bonus > 0 && 
            ` +${news.trust_breakdown.onchain_bonus.toFixed(1)} OnChain`}
          )
        </div>
      </div>
    </div>
  );
}
```

---

## ⏰ TIME-BASED LOGIC

### 1. Khi Nào Tính Enhanced Trust?

```python
# CÁCH 1: Realtime (khi crawl tin mới)
# Ưu điểm: Luôn fresh
# Nhược điểm: Signals có thể chưa có (tin xuất hiện trước signals)

# CÁCH 2: Batch Processing (mỗi 30 phút)
# Ưu điểm: Đảm bảo có đủ signals
# Nhược điểm: Delay 30 phút

# CÁCH 3: Hybrid (Recommended)
async def calculate_trust_hybrid(news_id: int, db: AsyncSession):
    """
    - Tính ngay khi crawl (best effort)
    - Re-calculate sau 30 phút nếu không có signals lúc đầu
    """
    news = await db.get(News, news_id)
    
    # Lần 1: Tính ngay
    signals = await get_relevant_signals(news.published_at, db)
    if signals:
        save_correlation(news, signals)
    else:
        # Schedule re-calculate sau 30 phút
        schedule_recalculation(news_id, delay_minutes=30)
```

### 2. Cache Strategy

```python
# Cache enhanced trust score trong news_signal_correlation table
# Chỉ re-calculate khi:
# 1. Có signals mới được thêm vào trong time window
# 2. Manual trigger từ admin
# 3. Source trust_score thay đổi
```

---

## 🚀 IMPLEMENTATION STEPS

### Phase 1: Database (1 ngày)
- [ ] Tạo bảng `news_signal_correlation`
- [ ] Migration script
- [ ] Indexes

### Phase 2: Backend Logic (2 ngày)
- [ ] `get_relevant_signals()` function
- [ ] `calculate_enhanced_trust()` function
- [ ] `extract_keywords()` function
- [ ] Update crawler to call calculation
- [ ] API endpoint modification

### Phase 3: Frontend (1 ngày)
- [ ] Update NewsCard component
- [ ] Trust score breakdown tooltip
- [ ] Sorting by enhanced trust

### Phase 4: Testing (1 ngày)
- [ ] Unit tests cho calculation logic
- [ ] Integration tests
- [ ] Performance testing với large dataset

### Phase 5: Monitoring (ongoing)
- [ ] Track accuracy của enhanced trust
- [ ] A/B testing với users
- [ ] Adjust weights dựa trên feedback

---

## 📈 EXPECTED RESULTS

1. **Tin tức tin cậy hơn**: Loại bỏ tin "nhiễu" không phù hợp với tín hiệu thị trường
2. **Cảnh báo sớm**: Tin trái chiều với signals → potential FUD/FOMO
3. **Better UX**: Users thấy tin chất lượng cao hơn ở top feed
4. **Data-driven**: Dựa trên dữ liệu thực tế thay vì chỉ nguồn tin

---

## ⚖️ TRADE-OFFS

**Pros:**
- ✅ Tin cậy hơn
- ✅ Data-driven
- ✅ Tự động hóa

**Cons:**
- ❌ Phức tạp hơn
- ❌ Phụ thuộc vào chất lượng signals
- ❌ Time window có thể không hoàn hảo (news lead/lag signals)

**Risk Mitigation:**
- Giữ `base_trust_score` làm fallback
- Cho phép admin override
- A/B test trước khi rollout full
