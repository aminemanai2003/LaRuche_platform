import { useEffect, useState } from 'react'
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native'
import { fetchMarket, type MarketData } from '../api/client'

export default function MarketScreen() {
  const [market, setMarket] = useState<MarketData | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetchMarket().then(setMarket).catch(() => setError(true))
  }, [])

  if (error) return <View style={s.container}><Text style={s.name}>Could not load market data.</Text></View>
  if (!market) return <View style={[s.container, { justifyContent: 'center' }]}><ActivityIndicator color="#a78bfa" /></View>

  return (
    <View style={s.container}>
      <FlatList
        data={market.quotes}
        keyExtractor={q => q.symbol}
        contentContainerStyle={s.list}
        ListHeaderComponent={<Text style={s.heading}>Market Data</Text>}
        numColumns={2}
        columnWrapperStyle={s.row}
        renderItem={({ item }) => (
          <View style={s.card}>
            <Text style={s.symbol}>{item.symbol}</Text>
            <Text style={s.name}>{item.name}</Text>
            <Text style={s.price}>
              {item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </Text>
            <Text style={[s.change, { color: item.change_pct >= 0 ? '#34d399' : '#f87171' }]}>
              {item.change_pct >= 0 ? '+' : ''}{item.change_pct.toFixed(2)}%
            </Text>
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
  row: { gap: 10, marginBottom: 10 },
  card: {
    flex: 1,
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
  },
  symbol: { fontSize: 11, color: '#94a3b8', marginBottom: 2 },
  name: { fontSize: 13, color: '#cbd5e1', marginBottom: 6 },
  price: { fontSize: 16, fontWeight: '700', color: '#fff', marginBottom: 2 },
  change: { fontSize: 12, fontWeight: '600' },
})
