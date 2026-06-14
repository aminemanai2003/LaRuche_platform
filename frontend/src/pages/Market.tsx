import { TrendingUp, TrendingDown } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getMarket } from '../api/client'

export default function Market() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['market'], queryFn: getMarket })

  if (isLoading) return <div className="p-6 text-slate-400 text-sm">Loading market data…</div>
  if (isError || !data) return <div className="p-6 text-red-400 text-sm">Could not load market data.</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-white">Market Data</h1>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {data.quotes.map(q => (
          <div key={q.symbol} className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs text-slate-400">{q.name}</p>
                <p className="text-lg font-bold text-white mt-1">
                  {q.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </div>
              <span className={`flex items-center gap-1 text-sm font-medium ${q.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {q.change_pct >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {q.change_pct >= 0 ? '+' : ''}{q.change_pct.toFixed(2)}%
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2">{q.symbol}</p>
          </div>
        ))}
      </div>

      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">Economic Indicators</h2>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {data.indicators.map(ind => (
            <div key={ind.key} className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs text-slate-400">{ind.name}</p>
              <p className="text-lg font-bold text-white">{ind.value}{ind.unit === '%' ? '%' : ` ${ind.unit}`}</p>
              <p className="text-xs text-slate-500">{ind.date}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
