import React, { useRef, useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import authService from '../services/auth'

const GOOGLE_ONLY = import.meta.env.VITE_GOOGLE_ONLY === 'true'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleClientId, setGoogleClientId] = useState('')
  const { login, googleLogin } = useAuth()
  const navigate = useNavigate()
  const googleRef = useRef(null)

  useEffect(() => {
    authService.getGoogleConfig()
      .then(cfg => setGoogleClientId(cfg.client_id || ''))
      .catch(() => setGoogleClientId(''))
  }, [])

  const handleGoogleCredential = async (response) => {
    setError('')
    setLoading(true)
    try {
      await googleLogin(response.credential)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Google sign-in failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!googleClientId || !googleRef.current) return
    if (!window.google) return

    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCredential
    })
    window.google.accounts.id.renderButton(googleRef.current, {
      theme: 'filled_black',
      size: 'large',
      text: 'continue_with',
      shape: 'pill',
      width: googleRef.current.clientWidth || 340
    })
  }, [googleClientId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Incorrect email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexGrow: 1, justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: '1rem' }}>
      <div className="glass-card" style={{ padding: '2.5rem', width: '100%', maxWidth: '420px' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontWeight: 600, color: 'var(--primary-color)' }}>Welcome Back</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Login to access funding & innovation tools.</p>

        {error && (
          <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', fontSize: '0.875rem', marginBottom: '1rem', fontWeight: 500 }}>
            {error}
          </div>
        )}

        {googleClientId && (
          <>
            <div ref={googleRef} style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }} />
            {!GOOGLE_ONLY && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                <span style={{ flexGrow: 1, height: '1px', backgroundColor: 'var(--border-color)' }} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>or</span>
                <span style={{ flexGrow: 1, height: '1px', backgroundColor: 'var(--border-color)' }} />
              </div>
            )}
          </>
        )}

        {GOOGLE_ONLY ? (
          <p style={{ marginTop: '0.25rem', marginBottom: '1.25rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
            Sign in with your Google account to access funding &amp; innovation tools.
          </p>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Email Address</label>
              <input className="input-field" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="name@domain.com" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Password</label>
              <input className="input-field" type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••" />
            </div>
            <button className="btn-primary" type="submit" disabled={loading} style={{ marginTop: '0.5rem', opacity: loading ? 0.7 : 1 }}>
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        )}

        {!googleClientId && (
          <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Sign-in is temporarily unavailable.
          </p>
        )}

        {GOOGLE_ONLY ? (
          <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
            First time here? Your account is created automatically the first time you sign in with Google.
          </p>
        ) : (
          <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
            Don't have an account? <Link to="/register" style={{ color: 'var(--primary-color)', textDecoration: 'none', fontWeight: 650 }}>Register here</Link>
          </p>
        )}
      </div>
    </div>
  )
}

export default Login