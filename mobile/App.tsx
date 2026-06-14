import { StatusBar } from 'expo-status-bar'
import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { Text } from 'react-native'
import DashboardScreen from './screens/DashboardScreen'
import ChatScreen from './screens/ChatScreen'
import PortfolioScreen from './screens/PortfolioScreen'
import MarketScreen from './screens/MarketScreen'
import { setToken } from './api/client'

// Dev: inject a bearer token so all API calls work without Keycloak
setToken('dev-token')

const Tab = createBottomTabNavigator()

const ICONS: Record<string, string> = {
  Dashboard: '📊',
  Portfolio: '💼',
  Market: '📈',
  Chat: '💬',
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: () => <Text style={{ fontSize: 18 }}>{ICONS[route.name]}</Text>,
          tabBarStyle: { backgroundColor: '#1e293b', borderTopColor: '#334155' },
          tabBarActiveTintColor: '#a78bfa',
          tabBarInactiveTintColor: '#64748b',
          headerStyle: { backgroundColor: '#0f172a' },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: '700' },
        })}
      >
        <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'WealthMesh' }} />
        <Tab.Screen name="Portfolio" component={PortfolioScreen} />
        <Tab.Screen name="Market" component={MarketScreen} />
        <Tab.Screen name="Chat" component={ChatScreen} options={{ title: 'AI Chat' }} />
      </Tab.Navigator>
    </NavigationContainer>
  )
}
