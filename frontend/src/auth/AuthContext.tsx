import { useEffect, useState, type ReactNode } from 'react'
import { setAuthToken } from '../api/client'
import { AuthContext, type AuthState } from './auth-context'
import kc, { initializeKeycloak } from './keycloak'

export function AuthProvider({ children }: { children: ReactNode }) {
  const devAuth = import.meta.env.VITE_DEV_AUTH === 'true'
  const [state, setState] = useState<AuthState>({
    ready: devAuth,
    authenticated: devAuth,
    token: devAuth ? 'dev-token' : null,
    username: devAuth ? 'advisor@wealthmesh.local' : null,
    roles: devAuth ? ['advisor'] : [],
    login: () => kc.login(),
    logout: () => kc.logout(),
  })

  useEffect(() => {
    if (devAuth) return

    let active = true
    initializeKeycloak().then(auth => {
      if (!active) return
      setState(current => ({
        ...current,
        ready: true,
        authenticated: auth,
        token: kc.token ?? null,
        username: kc.tokenParsed?.preferred_username ?? null,
        roles: (kc.tokenParsed?.realm_access?.roles as string[]) ?? [],
      }))
    })

    const interval = window.setInterval(() => {
      kc.updateToken(60).then(refreshed => {
        if (active && refreshed) {
          setState(current => ({ ...current, token: kc.token ?? null }))
        }
      })
    }, 60_000)

    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [devAuth])

  useEffect(() => {
    setAuthToken(state.token)
  }, [state.token])

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>
}
