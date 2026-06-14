import { createContext } from 'react'

export interface AuthState {
  ready: boolean
  authenticated: boolean
  token: string | null
  username: string | null
  roles: string[]
  login: () => void
  logout: () => void
}

export const AuthContext = createContext<AuthState>({
  ready: false,
  authenticated: false,
  token: null,
  username: null,
  roles: [],
  login: () => {},
  logout: () => {},
})
