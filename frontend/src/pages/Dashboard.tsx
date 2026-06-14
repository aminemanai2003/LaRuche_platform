import { useQuery } from '@tanstack/react-query'
import type { CSSProperties, ReactNode } from 'react'
import {
  BarChart3,
  BriefcaseBusiness,
  DollarSign,
  Globe2,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react'
import { getAllocation, getPortfolioSummary } from '../api/client'

const BAR_COLORS = ['#9b7cff', '#5eead4', '#6f8cff', '#e6b45e', '#858594']

export default function Dashboard() {
  const summary = useQuery({ queryKey: ['summary'], queryFn: getPortfolioSummary })
  const alloc = useQuery({ queryKey: ['allocation'], queryFn: getAllocation })

  if (summary.isLoading || alloc.isLoading) return <div className="loading-state">Loading portfolio intelligence...</div>
  if (summary.isError || alloc.isError || !summary.data || !alloc.data) {
    return <div className="error-state">Could not load portfolio data.</div>
  }

  const s = summary.data
  const metrics = [
    { label: 'Total AUM', value: s.aum_fmt, sub: `+${s.annualized_pct}% annualized`, icon: DollarSign, color: '#5ee6a8', glow: 'rgba(94,230,168,.12)' },
    { label: 'Time-weighted return', value: `${s.twr_pct}%`, sub: 'Since inception', icon: TrendingUp, color: '#9b7cff', glow: 'rgba(155,124,255,.15)' },
    { label: 'Internal rate of return', value: `${s.irr_pct.toFixed(2)}%`, sub: 'Portfolio IRR', icon: BarChart3, color: '#70a7ff', glow: 'rgba(92,150,255,.13)' },
    { label: 'Sharpe ratio', value: s.sharpe.toFixed(2), sub: `${s.volatility_pct}% volatility`, icon: ShieldCheck, color: '#e8b862', glow: 'rgba(232,184,98,.12)' },
  ]
  const geo = Object.entries(alloc.data.geography)
  const sectors = Object.entries(alloc.data.sector)

  return (
    <div className="page">
      <header className="page-intro">
        <div className="page-icon"><Globe2 className="h-5 w-5" /></div>
        <div>
          <p className="eyebrow">Live portfolio</p>
          <h1>Portfolio Overview</h1>
          <p>A clear view of performance, risk, and allocation across the family office.</p>
        </div>
      </header>

      <div className="metric-grid">
        {metrics.map(metric => (
          <article
            key={metric.label}
            className="surface-card metric-card"
            style={{ '--metric-glow': metric.glow } as CSSProperties}
          >
            <div className="metric-top">
              <span className="metric-label">{metric.label}</span>
              <span className="metric-icon" style={{ color: metric.color }}><metric.icon className="h-4 w-4" /></span>
            </div>
            <p className="metric-value" style={{ color: metric.color }}>{metric.value}</p>
            <p className="metric-sub">{metric.sub}</p>
          </article>
        ))}
      </div>

      <div className="data-grid">
        <BreakdownCard title="Geographic allocation" subtitle="Exposure by region" data={geo} />
        <BreakdownCard title="Sector allocation" subtitle="Capital by strategy" data={sectors} />
      </div>

      <div className="surface-card summary-strip">
        <SummaryStat icon={<BriefcaseBusiness className="h-4 w-4" />} label="Active deals" value={String(s.num_active)} />
        <SummaryStat icon={<DollarSign className="h-4 w-4" />} label="Total profit" value={s.profit_fmt} />
        <SummaryStat icon={<ShieldCheck className="h-4 w-4" />} label="Volatility" value={`${s.volatility_pct}%`} />
      </div>
    </div>
  )
}

function BreakdownCard({
  title,
  subtitle,
  data,
}: {
  title: string
  subtitle: string
  data: [string, number][]
}) {
  return (
    <section className="surface-card data-panel">
      <div className="data-panel-header">
        <h2>{title}</h2>
        <span>{subtitle}</span>
      </div>
      {data.map(([label, pct], index) => (
        <div className="bar-row" key={label}>
          <span className="bar-label">{label}</span>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{ width: `${pct}%`, background: BAR_COLORS[index % BAR_COLORS.length], color: BAR_COLORS[index % BAR_COLORS.length] }}
            />
          </div>
          <span className="bar-value">{pct}%</span>
        </div>
      ))}
    </section>
  )
}

function SummaryStat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="summary-stat">
      <span style={{ color: '#9b7cff', display: 'grid', placeItems: 'center', marginBottom: 8 }}>{icon}</span>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  )
}
