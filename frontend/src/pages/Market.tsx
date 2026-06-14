import { useQuery } from '@tanstack/react-query'
import { Activity, TrendingDown, TrendingUp } from 'lucide-react'
import { getMarket } from '../api/client'

export default function Market() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['market'], queryFn: getMarket })

  if (isLoading) return <div className="loading-state">Loading market signals...</div>
  if (isError || !data) return <div className="error-state">Could not load market data.</div>

  return (
    <div className="page">
      <header className="page-intro">
        <div className="page-icon"><Activity className="h-5 w-5" /></div>
        <div>
          <p className="eyebrow">Macro pulse</p>
          <h1>Market Data</h1>
          <p>Key public-market signals and economic indicators in one focused view.</p>
        </div>
      </header>

      <div className="market-grid">
        {data.quotes.map(quote => (
          <article key={quote.symbol} className="surface-card quote-card">
            <span className="quote-symbol">{quote.symbol}</span>
            <p className="quote-name">{quote.name}</p>
            <div className="quote-line">
              <strong className="quote-price">
                {quote.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </strong>
              <span className={`quote-change ${quote.change_pct >= 0 ? 'positive' : 'negative'}`}>
                {quote.change_pct >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {quote.change_pct >= 0 ? '+' : ''}{quote.change_pct.toFixed(2)}%
              </span>
            </div>
          </article>
        ))}
      </div>

      <section className="surface-card data-panel" style={{ marginTop: 14 }}>
        <div className="data-panel-header">
          <h2>Economic indicators</h2>
          <span>Latest canonical readings</span>
        </div>
        <div className="indicator-grid">
          {data.indicators.map(indicator => (
            <div key={indicator.key} className="indicator-card">
              <span>{indicator.name}</span>
              <strong>{indicator.value}{indicator.unit === '%' ? '%' : ` ${indicator.unit}`}</strong>
              <small>{indicator.date}</small>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
