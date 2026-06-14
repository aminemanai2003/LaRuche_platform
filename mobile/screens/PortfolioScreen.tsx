import { useEffect, useState } from 'react'
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native'
import { fetchDeals, type Deal } from '../api/client'

export default function PortfolioScreen() {
  const [deals, setDeals] = useState<Deal[] | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetchDeals().then(setDeals).catch(() => setError(true))
  }, [])

  if (error) return <View style={s.container}><Text style={s.sector}>Could not load deals.</Text></View>
  if (!deals) return <View style={[s.container, { justifyContent: 'center' }]}><ActivityIndicator color="#a78bfa" /></View>

  return (
    <View style={s.container}>
      <FlatList
        data={deals}
        keyExtractor={d => d.name}
        contentContainerStyle={s.list}
        ListHeaderComponent={<Text style={s.heading}>Active Deals</Text>}
        renderItem={({ item }) => (
          <View style={s.card}>
            <View style={s.cardHeader}>
              <Text style={s.name} numberOfLines={1}>{item.name}</Text>
              <Text style={[s.twr, { color: item.twr >= 0 ? '#34d399' : '#f87171' }]}>
                {item.twr >= 0 ? '+' : ''}{item.twr.toFixed(1)}%
              </Text>
            </View>
            <View style={s.cardFooter}>
              <Text style={s.sector}>{item.sector}</Text>
              <Text style={s.aum}>${item.aum.toFixed(1)}M AUM</Text>
            </View>
          </View>
        )}
      />
    </View>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  list: { padding: 16, gap: 10 },
  heading: { fontSize: 22, fontWeight: '700', color: '#fff', marginBottom: 8 },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
    gap: 6,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  name: { fontSize: 14, fontWeight: '600', color: '#fff', flex: 1, marginRight: 8 },
  twr: { fontSize: 14, fontWeight: '700' },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between' },
  sector: { fontSize: 12, color: '#94a3b8' },
  aum: { fontSize: 12, color: '#94a3b8' },
})
