import { ShieldCheck, Sparkles } from 'lucide-react'
import { useAuth } from '../auth/useAuth'

export default function Login() {
  const { login } = useAuth()

  return (
    <div className="login-screen">
      <section className="login-visual">
        <div className="login-mesh" />
        <div className="login-copy">
          <p className="eyebrow">Private banking, reimagined</p>
          <h1>Intelligence for every wealth decision.</h1>
          <p>
            One secure workspace for portfolio analytics, market context, document intelligence,
            conversational advice, and natural voice interaction.
          </p>
        </div>
      </section>

      <section className="login-form-wrap">
        <div className="glass-panel login-card">
          <div className="brand-block">
            <div className="brand-mark"><Sparkles className="h-4 w-4" /></div>
            <div>
              <h1 className="brand-name">WealthMesh</h1>
              <p className="brand-caption">Private intelligence</p>
            </div>
          </div>
          <h2>Welcome back</h2>
          <p>Sign in to enter your secure advisory workspace.</p>
          <button onClick={login} className="primary-button login-button">
            Sign in with SSO
          </button>
          <div className="login-security">
            <ShieldCheck className="h-3.5 w-3.5" />
            Secured with Keycloak PKCE
          </div>
        </div>
      </section>
    </div>
  )
}
