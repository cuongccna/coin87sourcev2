import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Coin87 Crypto News'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

export default async function Image({ params }: { params: { id: string } }) {
  // Fetch news data
  const newsId = params.id
  
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/news/${newsId}`)
    const news = await res.json()
    
    // Determine sentiment badge
    const sentimentColor = 
      news.sentiment_label === 'Bullish' ? '#10b981' :
      news.sentiment_label === 'Bearish' ? '#ef4444' :
      '#6b7280'
    
    return new ImageResponse(
      (
        <div
          style={{
            fontSize: 48,
            background: 'linear-gradient(to bottom right, #1e293b, #0f172a)',
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            padding: '60px',
          }}
        >
          {/* Title */}
          <div
            style={{
              fontSize: 56,
              fontWeight: 'bold',
              color: 'white',
              lineHeight: 1.2,
              marginBottom: 20,
            }}
          >
            {news.title.substring(0, 120)}...
          </div>
          
          {/* Sentiment Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 20,
            }}
          >
            <div
              style={{
                background: sentimentColor,
                color: 'white',
                padding: '12px 32px',
                borderRadius: 8,
                fontSize: 32,
                fontWeight: 'bold',
              }}
            >
              {news.sentiment_label}
            </div>
            
            {/* Coins */}
            {news.coins_mentioned && news.coins_mentioned.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  gap: 12,
                }}
              >
                {news.coins_mentioned.slice(0, 3).map((coin: string) => (
                  <div
                    key={coin}
                    style={{
                      background: '#334155',
                      color: '#fbbf24',
                      padding: '8px 20px',
                      borderRadius: 6,
                      fontSize: 24,
                    }}
                  >
                    ${coin}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              alignItems: 'center',
              marginTop: 'auto',
            }}
          >
            <div
              style={{
                fontSize: 32,
                color: '#94a3b8',
              }}
            >
              Read on Coin87
            </div>
            <div
              style={{
                fontSize: 48,
                fontWeight: 'bold',
                color: '#fbbf24',
              }}
            >
              C87
            </div>
          </div>
        </div>
      ),
      {
        ...size,
      }
    )
  } catch (error) {
    // Fallback OG image
    return new ImageResponse(
      (
        <div
          style={{
            fontSize: 64,
            background: 'linear-gradient(to bottom right, #1e293b, #0f172a)',
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fbbf24',
            fontWeight: 'bold',
          }}
        >
          Coin87 Crypto News
        </div>
      ),
      {
        ...size,
      }
    )
  }
}
