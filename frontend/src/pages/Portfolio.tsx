import { TrendingUp, TrendingDown } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getDeals } from '../api/client'

export default function Portfolio() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['deals'], queryFn: getDeals })

  if (isLoading) return <div className="p-6 text-slate-400 text-sm">Loading deals…</div>
  if (isError || !data) return <div className="p-6 text-red-400 text-sm">Could not load deals.</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-white">Portfolio Deals</h1>

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase">
              <th className="text-left px-4 py-3">Deal</th>
              <th className="text-left px-4 py-3">Sector</th>
              <th className="text-left px-4 py-3">Geo</th>
              <th className="text-right px-4 py-3">AUM ($M)</th>
              <th className="text-right px-4 py-3">TWR (%)</th>
              <th className="text-left px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map(d => (
              <tr key={d.name} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                <td className="px-4 py-3 text-white font-medium">{d.name}</td>
                <td className="px-4 py-3 text-slate-300">{d.sector}</td>
                <td className="px-4 py-3 text-slate-300">{d.geo}</td>
                <td className="px-4 py-3 text-right text-white">{d.aum.toFixed(1)}</td>
                <td className="px-4 py-3 text-right">
                  <span className={`flex items-center justify-end gap-1 ${d.twr >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {d.twr >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {d.twr.toFixed(1)}%
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="bg-emerald-900/40 text-emerald-400 text-xs px-2 py-0.5 rounded-full">
                    {d.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
