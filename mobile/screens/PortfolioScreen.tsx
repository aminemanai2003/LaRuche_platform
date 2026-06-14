import { View, Text, FlatList, StyleSheet } from 'react-native'

const DEALS = [
  { id: '1', name: 'Wella Beauty Holdings', sector: 'Consumer', aum: 3.2, twr: 42.1 },
  { id: '2', name: 'Project Taka', sector: 'Real Estate', aum: 2.8, twr: 28.5 },
  { id: '3', name: 'NA Tech Fund IV', sector: 'Private Equity', aum: 2.1, twr: 65.3 },
  { id: '4', name: 'APAC Logistics Hub', sector: 'Real Estate', aum: 1.9, twr: 19.2 },
  { id: '5', name: 'EU Green Bond', sector: 'Credit', aum: 1.5, twr: 11.0 },
  { id: '6', name: 'SEA Growth Fund', sector: 'Equities', aum: 1.4, twr: 33.7 },
]

export default function PortfolioScreen() {
  return (
    <View style={s.container}>
      <FlatList
        data={DEALS}
        keyExtractor={d => d.id}
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
