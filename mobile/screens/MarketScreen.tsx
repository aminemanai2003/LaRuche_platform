import { View, Text, FlatList, StyleSheet } from 'react-native'

const QUOTES = [
  { id: 'SPX', name: 'S&P 500', price: 5247.49, change: 0.42 },
  { id: 'AAPL', name: 'Apple', price: 189.30, change: -0.18 },
  { id: 'BTC', name: 'Bitcoin', price: 67450.0, change: 2.33 },
  { id: 'GLD', name: 'Gold (oz)', price: 2328.60, change: 0.15 },
  { id: 'TSLA', name: 'Tesla', price: 175.22, change: 1.05 },
  { id: 'USDEUR', name: 'USD/EUR', price: 0.9285, change: -0.05 },
]

export default function MarketScreen() {
  return (
    <View style={s.container}>
      <FlatList
        data={QUOTES}
        keyExtractor={q => q.id}
        contentContainerStyle={s.list}
        ListHeaderComponent={<Text style={s.heading}>Market Data</Text>}
        numColumns={2}
        columnWrapperStyle={s.row}
        renderItem={({ item }) => (
          <View style={s.card}>
            <Text style={s.symbol}>{item.id}</Text>
            <Text style={s.name}>{item.name}</Text>
            <Text style={s.price}>
              {item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </Text>
            <Text style={[s.change, { color: item.change >= 0 ? '#34d399' : '#f87171' }]}>
              {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
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
