import axios from 'axios'

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000'

const api = axios.create({ baseURL: API_URL })

let _token: string | null = null

export function setToken(t: string | null) {
  _token = t
  if (t) api.defaults.headers.common['Authorization'] = `Bearer ${t}`
  else delete api.defaults.headers.common['Authorization']
}

export function getToken() {
  return _token
}

export async function fetchMe() {
  const { data } = await api.get('/api/me')
  return data as { user_id: string; email: string; roles: string[] }
}

// ── Portfolio & market data ───────────────────────────────────────────────
export interface PortfolioSummary {
  aum_fmt: string
  twr_pct: number
  annualized_pct: number
  irr_pct: number
  sharpe: number
  volatility_pct: number
  profit_fmt: string
  num_deals: number
  num_active: number
}
export interface Deal {
  name: string
  sector: string
  geo: string
  status: string
  aum: number
  twr: number
}
export interface MarketData {
  quotes: { symbol: string; name: string; price: number; change_pct: number }[]
  indicators: { key: string; name: string; value: number; unit: string; date: string }[]
}

export async function fetchSummary() {
  const { data } = await api.get('/api/portfolio/summary')
  return data as PortfolioSummary
}
export async function fetchAllocation() {
  const { data } = await api.get('/api/portfolio/allocation')
  return data as { geography: Record<string, number>; sector: Record<string, number> }
}
export async function fetchDeals() {
  const { data } = await api.get('/api/portfolio/deals')
  return data as Deal[]
}
export async function fetchMarket() {
  const { data } = await api.get('/api/market')
  return data as MarketData
}

export async function* streamChat(
  message: string,
  conversationId: string,
): AsyncGenerator<string> {
  const resp = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(_token ? { Authorization: `Bearer ${_token}` } : {}),
    },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })

  if (!resp.ok || !resp.body) throw new Error(`Chat error: ${resp.status}`)

  const reader = resp.body.getReader()
  const dec = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('data: ') && !line.includes('[DONE]')) {
        try {
          const payload = JSON.parse(line.slice(6))
          if (payload.token) yield payload.token as string
        } catch {
          // ignore
        }
      }
    }
  }
}

export default api
