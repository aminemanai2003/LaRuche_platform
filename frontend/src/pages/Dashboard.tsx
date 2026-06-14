import { TrendingUp, DollarSign, BarChart3, Globe } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getPortfolioSummary, getAllocation } from '../api/client'

const BAR_COLORS = ['bg-blue-500', 'bg-emerald-500', 'bg-purple-500', 'bg-amber-500', 'bg-slate-500']

export default function Dashboard() {
  const summary = useQuery({ queryKey: ['summary'], queryFn: getPortfolioSummary })
  const alloc = useQuery({ queryKey: ['allocation'], queryFn: getAllocation })

  if (summary.isLoading || alloc.isLoading) {
    return <div className="p-6 text-slate-400 text-sm">Loading portfolio…</div>
  }
  if (summary.isError || alloc.isError || !summary.data || !alloc.data) {
    return <div className="p-6 text-red-400 text-sm">Could not load portfolio data.</div>
  }

  const s = summary.data
  const metrics = [
    { label: 'Total AUM', value: s.aum_fmt, sub: `+${s.annualized_pct}% annualized`, icon: DollarSign, color: 'text-emerald-400' },
    { label: 'TWR', value: `${s.twr_pct}%`, sub: 'Since inception', icon: TrendingUp, color: 'text-blue-400' },
    { label: 'IRR', value: `${s.irr_pct.toFixed(2)}%`, sub: 'Internal Rate of Return', icon: BarChart3, color: 'text-purple-400' },
    { label: 'Sharpe Ratio', value: s.sharpe.toFixed(2), sub: `Vol: ${s.volatility_pct}%`, icon: Globe, color: 'text-amber-400' },
  ]
  const geo = Object.entries(alloc.data.geography).map(([label, pct], i) => ({ label, pct, color: BAR_COLORS[i % BAR_COLORS.length] }))
  const sectors = Object.entries(alloc.data.sector).map(([label, pct], i) => ({ label, pct, color: BAR_COLORS[i % BAR_COLORS.length] }))

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-white">Portfolio Overview</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map(m => (
          <div key={m.label} className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <m.icon className={`w-4 h-4 ${m.color}`} />
              <span className="text-xs text-slate-400">{m.label}</span>
            </div>
            <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
            <p className="text-xs text-slate-400 mt-1">{m.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <BreakdownCard title="Geographic Allocation" data={geo} />
        <BreakdownCard title="Sector Allocation" data={sectors} />
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">Portfolio Summary</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <Stat label="Active Deals" value={String(s.num_active)} />
          <Stat label="Total Profit" value={s.profit_fmt} />
          <Stat label="Volatility" value={`${s.volatility_pct}%`} />
        </div>
      </div>
    </div>
  )
}

type Row = { label: string; pct: number; color: string }

function BreakdownCard({ title, data }: { title: string; data: Row[] }) {
  return (
    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
      <h2 className="text-sm font-semibold text-slate-300 mb-3">{title}</h2>
      <div className="space-y-2">
        {data.map(d => (
          <div key={d.label} className="flex items-center gap-3">
            <span className="text-xs text-slate-400 w-28 shrink-0">{d.label}</span>
            <div className="flex-1 bg-slate-700 rounded-full h-2">
              <div className={`${d.color} h-2 rounded-full`} style={{ width: `${d.pct}%` }} />
            </div>
            <span className="text-xs text-slate-300 w-8 text-right">{d.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-lg font-bold text-white">{value}</p>
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  )
}
