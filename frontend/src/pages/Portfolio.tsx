import { useQuery } from '@tanstack/react-query'
import { BriefcaseBusiness, TrendingDown, TrendingUp } from 'lucide-react'
import { getDeals } from '../api/client'

export default function Portfolio() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['deals'], queryFn: getDeals })

  if (isLoading) return <div className="loading-state">Loading deal intelligence...</div>
  if (isError || !data) return <div className="error-state">Could not load deals.</div>

  return (
    <div className="page">
      <header className="page-intro">
        <div className="page-icon"><BriefcaseBusiness className="h-5 w-5" /></div>
        <div>
          <p className="eyebrow">Private markets</p>
          <h1>Portfolio Deals</h1>
          <p>Monitor deployed capital, realized outcomes, and current performance.</p>
        </div>
      </header>

      <section className="surface-card table-shell">
        <div className="table-toolbar">
          <div>
            <h2 className="table-title">Deal book</h2>
            <p>{data.length} representative investments from the canonical portfolio</p>
          </div>
          <span className="status-pill">Live data</span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Deal</th>
              <th>Sector</th>
              <th>Geography</th>
              <th style={{ textAlign: 'right' }}>AUM ($M)</th>
              <th style={{ textAlign: 'right' }}>TWR</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map(deal => (
              <tr key={deal.name}>
                <td className="deal-name">{deal.name}</td>
                <td>{deal.sector}</td>
                <td>{deal.geo}</td>
                <td style={{ textAlign: 'right', color: '#e4e2e9' }}>{deal.aum.toFixed(2)}</td>
                <td style={{ textAlign: 'right' }}>
                  <span className={`quote-change ${deal.twr >= 0 ? 'positive' : 'negative'}`}>
                    {deal.twr >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    {deal.twr.toFixed(1)}%
                  </span>
                </td>
                <td><span className="status-pill">{deal.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
