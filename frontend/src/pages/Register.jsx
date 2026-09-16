import React, { useRef, useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import authService from '../services/auth'
import SplitAuthLayout from '../components/auth/SplitAuthLayout'

const GOOGLE_ONLY = import.meta.env.VITE_GOOGLE_ONLY === 'true'

function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('researcher')
  const [fieldError, setFieldError] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleClientId, setGoogleClientId] = useState('')
  const [googleReady, setGoogleReady] = useState(false)
  const { googleLogin } = useAuth()
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
    setFieldError('')

    if (password !== confirmPassword) {
      setFieldError('Passwords do not match.')
      return
    }
    if (password.length < 6) {
      setFieldError('Password must be at least 6 characters long.')
      return
    }

    setLoading(true)
    try {
      await authService.register(email, password, fullName, role)
      setSuccess('Registration successful! Redirecting to login...')
      setTimeout(() => {
        navigate('/login')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  const head = (
    <div className="auth-form-card">
      <h2>Create Account</h2>
      <p className="auth-card-sub">Join the funding &amp; innovation network.</p>

      {error && (
        <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', fontSize: '0.875rem', marginBottom: '1rem', fontWeight: 500 }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#6ee7b7', fontSize: '0.875rem', marginBottom: '1rem', fontWeight: 500 }}>
          {success}
        </div>
      )}

      {googleClientId && googleReady && (
        <>
          <div ref={googleRef} className="google-btn-wrapper" style={{ display: 'flex', justifyContent: 'center' }} />
          {!GOOGLE_ONLY && <div className="auth-divider"><span>or sign up with email</span></div>}
        </>
      )}

      {GOOGLE_ONLY ? (
        <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Your Infera account is created automatically the first time you sign in with Google.
        </p>
      ) : (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Full Name</label>
            <input className="input-field" type="text" value={fullName} onChange={e => setFullName(e.target.value)} required placeholder="Dr. Jane Doe" />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Email Address</label>
            <input className="input-field" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="name@domain.com" />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Password</label>
            <input className="input-field" type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Min 6 characters" />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Confirm Password</label>
            <input className="input-field" type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required placeholder="Re-enter password" />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Account Role</label>
            <select className="select-field" value={role} onChange={e => setRole(e.target.value)}>
              <option value="researcher">Researcher / Innovator</option>
              <option value="funder">Investor / Funder</option>
              <option value="admin">Administrator</option>
            </select>
          </div>

          {fieldError && (
            <div style={{ padding: '0.75rem', borderRadius: '6px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d', fontSize: '0.875rem', fontWeight: 500 }}>
              {fieldError}
            </div>
          )}

          <button className="btn-primary" type="submit" disabled={loading} style={{ marginTop: '0.5rem', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>
      )}

      {!googleClientId && (
        <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
          Loading sign-up…
        </p>
      )}
    </div>
  )

  const foot = (
    <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
      Already have an account? <Link to="/login" style={{ color: 'var(--primary-color)', textDecoration: 'none', fontWeight: 650 }}>Log in here</Link>
    </p>
  )

  return (
    <SplitAuthLayout head={head} foot={foot} />
  )
}

export default Register