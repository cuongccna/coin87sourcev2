"""
Migration: Tạo bảng news_signal_correlation
Mục đích: Lưu enhanced trust score từ trading signals
"""

import asyncio
from sqlalchemy import text
from app.db.session import engine

async def create_news_signal_correlation_table():
    """Tạo bảng liên kết news với trading signals"""
    
    async with engine.begin() as conn:
        # 1. Tạo bảng
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS news_signal_correlation (
                id SERIAL PRIMARY KEY,
                news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
                smart_money_signal_id INTEGER REFERENCES smart_money_signals(id) ON DELETE SET NULL,
                sentiment_report_id INTEGER REFERENCES sentiment_reports(id) ON DELETE SET NULL,
                onchain_intelligence_id INTEGER REFERENCES onchain_intelligence(id) ON DELETE SET NULL,
                enhanced_trust_score FLOAT NOT NULL,
                base_trust_score FLOAT NOT NULL,
                smart_money_bonus FLOAT DEFAULT 0.0,
                sentiment_bonus FLOAT DEFAULT 0.0,
                onchain_bonus FLOAT DEFAULT 0.0,
                time_diff_seconds INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(news_id)
            )
        """))
        
        # 2. Tạo indexes
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_news_signal_correlation_news 
                ON news_signal_correlation(news_id)
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_news_signal_correlation_enhanced_trust 
                ON news_signal_correlation(enhanced_trust_score DESC)
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_news_signal_correlation_created 
                ON news_signal_correlation(created_at DESC)
        """))
        
        # 3. Tạo function
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_news_signal_correlation_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """))
        
        # 4. Tạo trigger
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS trg_update_news_signal_correlation_timestamp 
                ON news_signal_correlation
        """))
        
        await conn.execute(text("""
            CREATE TRIGGER trg_update_news_signal_correlation_timestamp
                BEFORE UPDATE ON news_signal_correlation
                FOR EACH ROW
                EXECUTE FUNCTION update_news_signal_correlation_timestamp()
        """))
        
        print("✅ Tạo bảng news_signal_correlation thành công")
        
        # Verify
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'news_signal_correlation'
            ORDER BY ordinal_position
        """))
        
        print("\n📋 Cấu trúc bảng:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
        
        # Check indexes
        indexes = await conn.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'news_signal_correlation'
        """))
        
        print("\n🔍 Indexes:")
        for idx in indexes:
            print(f"  - {idx[0]}")

if __name__ == "__main__":
    print("🚀 Bắt đầu migration: news_signal_correlation table")
    asyncio.run(create_news_signal_correlation_table())
    print("\n✅ Migration hoàn tất!")
