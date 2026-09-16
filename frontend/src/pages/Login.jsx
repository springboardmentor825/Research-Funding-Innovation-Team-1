import React, { useRef, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import authService from '../services/auth'
import SplitAuthLayout from '../components/auth/SplitAuthLayout'

const GOOGLE_ONLY = import.meta.env.VITE_GOOGLE_ONLY === 'true'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleClientId, setGoogleClientId] = useState('')
  const [googleReady, setGoogleReady] = useState(false)
  const { login, googleLogin } = useAuth()
  const navigate = useNavigate()
  const googleRef = useRef(null)

  useEffect(() => {
    authService.getGoogleConfig()
      .then(cfg => setGoogleClientId(cfg.client_id || ''))
      .catch(() => setGoogleClientId(''))
  }, [])

  useEffect(() => {
    if (window.google) { setGoogleReady(true); return }
    const t = setInterval(() => {
      if (window.google) { setGoogleReady(true); clearInterval(t) }
    }, 200)
    return () => clearInterval(t)
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
    if (!googleClientId || !googleReady || !googleRef.current) return

    if (googleRef.current.firstElementChild) {
      googleRef.current.innerHTML = ''
    }

    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCredential
    })
    window.google.accounts.id.renderButton(googleRef.current, {
      theme: 'filled_black',
      size: 'large',
      text: 'continue_with',
      shape: 'rectangular',
      logo_alignment: 'left',
      width: 360
    })
  }, [googleClientId, googleReady])

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

  const head = (
    <div className="auth-form-card">
      <h2>Welcome Back</h2>
      <p className="auth-card-sub">Login to access funding &amp; innovation tools.</p>

      {error && (
        <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', fontSize: '0.875rem', marginBottom: '1rem', fontWeight: 500 }}>
          {error}
        </div>
      )}

      {googleClientId && googleReady && (
        <>
          <div ref={googleRef} className="google-btn-wrapper" style={{ display: 'flex', justifyContent: 'center' }} />
          {!GOOGLE_ONLY && <div className="auth-divider"><span>or sign in with email</span></div>}
        </>
      )}

      {GOOGLE_ONLY ? (
        <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
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
          Loading sign-in…
        </p>
      )}
    </div>
  )

  const foot = GOOGLE_ONLY ? (
    <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
      First time here? Your account is created automatically the first time you sign in with Google.
    </p>
  ) : (
    <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
      Don't have an account? <Link to="/register" style={{ color: 'var(--primary-color)', textDecoration: 'none', fontWeight: 650 }}>Register here</Link>
    </p>
  )

  return (
    <SplitAuthLayout head={head} foot={foot} />
  )
}

export default Login