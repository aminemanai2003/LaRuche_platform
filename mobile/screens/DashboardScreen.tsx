import { useEffect, useState } from 'react'
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from 'react-native'
import { fetchSummary, fetchAllocation, type PortfolioSummary } from '../api/client'

const BAR_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#6b7280']

export default function DashboardScreen() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [geo, setGeo] = useState<{ label: string; pct: number; color: string }[]>([])
  const [error, setError] = useState(false)

  useEffect(() => {
    Promise.all([fetchSummary(), fetchAllocation()])
      .then(([s, a]) => {
        setSummary(s)
        setGeo(
          Object.entries(a.geography).map(([label, pct], i) => ({
            label,
            pct,
            color: BAR_COLORS[i % BAR_COLORS.length],
          })),
        )
      })
      .catch(() => setError(true))
  }, [])

  if (error) return <View style={s.container}><Text style={s.cardSub}>Could not load data.</Text></View>
  if (!summary) return <View style={[s.container, { justifyContent: 'center' }]}><ActivityIndicator color="#a78bfa" /></View>

  const METRICS = [
    { label: 'Total AUM', value: summary.aum_fmt, sub: `+${summary.annualized_pct}% annualized`, color: '#34d399' },
    { label: 'TWR', value: `${summary.twr_pct}%`, sub: 'Since inception', color: '#60a5fa' },
    { label: 'IRR', value: `${summary.irr_pct.toFixed(2)}%`, sub: 'Internal Rate of Return', color: '#a78bfa' },
    { label: 'Sharpe Ratio', value: summary.sharpe.toFixed(2), sub: `Volatility: ${summary.volatility_pct}%`, color: '#fbbf24' },
  ]
  const GEO = geo

  return (
    <ScrollView style={s.container} contentContainerStyle={s.content}>
      <Text style={s.heading}>Portfolio Overview</Text>

      {/* KPI Cards */}
      <View style={s.grid}>
        {METRICS.map(m => (
          <View key={m.label} style={s.card}>
            <Text style={s.cardLabel}>{m.label}</Text>
            <Text style={[s.cardValue, { color: m.color }]}>{m.value}</Text>
            <Text style={s.cardSub}>{m.sub}</Text>
          </View>
        ))}
      </View>

      {/* Geography */}
      <View style={s.section}>
        <Text style={s.sectionTitle}>Geographic Allocation</Text>
        {GEO.map(g => (
          <View key={g.label} style={s.barRow}>
            <Text style={s.barLabel}>{g.label}</Text>
            <View style={s.barTrack}>
              <View style={[s.barFill, { width: `${g.pct}%` as any, backgroundColor: g.color }]} />
            </View>
            <Text style={s.barPct}>{g.pct}%</Text>
          </View>
        ))}
      </View>

      {/* Summary row */}
      <View style={[s.section, s.rowSection]}>
        <Stat label="Deals" value={String(summary.num_active)} />
        <Stat label="Profit" value={summary.profit_fmt} />
        <Stat label="Volatility" value={`${summary.volatility_pct}%`} />
      </View>
    </ScrollView>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={s.statBox}>
      <Text style={s.statValue}>{value}</Text>
      <Text style={s.statLabel}>{label}</Text>
    </View>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  content: { padding: 16, gap: 16 },
  heading: { fontSize: 22, fontWeight: '700', color: '#fff', marginBottom: 4 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    width: '47%',
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardLabel: { fontSize: 11, color: '#94a3b8', marginBottom: 4 },
  cardValue: { fontSize: 20, fontWeight: '700' },
  cardSub: { fontSize: 10, color: '#64748b', marginTop: 2 },
  section: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 10,
  },
  sectionTitle: { fontSize: 13, fontWeight: '600', color: '#cbd5e1', marginBottom: 4 },
  barRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  barLabel: { fontSize: 11, color: '#94a3b8', width: 100 },
  barTrack: { flex: 1, height: 6, backgroundColor: '#334155', borderRadius: 3 },
  barFill: { height: 6, borderRadius: 3 },
  barPct: { fontSize: 11, color: '#cbd5e1', width: 32, textAlign: 'right' },
  rowSection: { flexDirection: 'row', justifyContent: 'space-around' },
  statBox: { alignItems: 'center' },
  statValue: { fontSize: 18, fontWeight: '700', color: '#fff' },
  statLabel: { fontSize: 11, color: '#94a3b8' },
})
