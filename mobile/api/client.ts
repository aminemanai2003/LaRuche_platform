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
