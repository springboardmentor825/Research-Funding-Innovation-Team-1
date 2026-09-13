import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Sparkles, Lock, Mail, UserCheck, ArrowRight, ShieldCheck } from 'lucide-react'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [selectedRole, setSelectedRole] = useState('researcher')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const { login, googleAuth } = useAuth()
  const navigate = useNavigate()

  const handleRoleRedirect = (role) => {
    switch (role) {
      case 'startup_founder':
        navigate('/startup/dashboard')
        break
      case 'administrator':
        navigate('/admin/dashboard')
        break
      case 'researcher':
      default:
        navigate('/dashboard')
        break
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(email, password, selectedRole)
      if (res.status === 'success' && res.user) {
        handleRoleRedirect(res.user.role)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Selected role does not match your account role.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError('')
    setGoogleLoading(true)
    try {
      // Simulate/Trigger Google OAuth authentication
      const demoEmail = email || `user_${Date.now().toString().slice(-4)}@example.com`
      const demoName = demoEmail.split('@')[0].replace('_', ' ').toUpperCase()
      const res = await googleAuth(demoEmail, demoName)
      
      if (res.status === 'pending_role_selection') {
        navigate('/select-role')
      } else if (res.status === 'success' && res.user) {
        handleRoleRedirect(res.user.role)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Google Authentication failed. Please try again.')
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      width: '100%',
      padding: '1.5rem',
      backgroundColor: 'var(--bg-dark)'
    }}>
      <div 
        className="ai-card glow-animation" 
        style={{ 
          padding: '2.5rem', 
          width: '100%', 
          maxWidth: '460px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid var(--border-glow)'
        }}
      >
        {/* Brand Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.5rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)'
          }}>
            <Sparkles size={24} color="#FFFFFF" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F8FAFC', margin: 0 }}>
              AI Fund Platform
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)', fontWeight: 500 }}>
              Research & Innovation Intelligence
            </span>
          </div>
        </div>

        <h3 style={{ fontSize: '1.25rem', color: '#F8FAFC', fontWeight: 700, marginBottom: '0.35rem' }}>
          Role-Based Sign In
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
          Select your registered role and enter credentials to access your dashboard.
        </p>

        {error && (
          <div style={{
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#EF4444',
            fontSize: '0.85rem',
            marginBottom: '1.25rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
          {/* Account Role Selection */}
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Account Role
            </label>
            <div style={{ position: 'relative' }}>
              <UserCheck size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              <select
                className="ai-input"
                value={selectedRole}
                onChange={e => setSelectedRole(e.target.value)}
                style={{ paddingLeft: '2.5rem', backgroundColor: '#0F172A', color: '#F8FAFC' }}
              >
                <option value="researcher">Researcher</option>
                <option value="startup_founder">Startup Founder</option>
                <option value="administrator">Administrator</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                className="ai-input" 
                type="email" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                required 
                placeholder="user@university.edu" 
                style={{ paddingLeft: '2.5rem' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                className="ai-input" 
                type="password" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                required 
                placeholder="••••••••" 
                style={{ paddingLeft: '2.5rem' }}
              />
            </div>
          </div>

          <button 
            className="btn-ai-primary" 
            type="submit" 
            disabled={loading || googleLoading} 
            style={{ marginTop: '0.5rem', width: '100%', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Authenticating Role...' : 'Sign In to Dashboard'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          margin: '1.5rem 0',
          color: 'var(--text-secondary)',
          fontSize: '0.8rem'
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.1)' }} />
          <span>OR</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'rgba(255,255,255,0.1)' }} />
        </div>

        {/* Google OAuth Button */}
        <button
          type="button"
          onClick={handleGoogleLogin}
          disabled={googleLoading || loading}
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            backgroundColor: '#1E293B',
            border: '1px solid var(--border-glow)',
            color: '#F8FAFC',
            fontWeight: 600,
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.65rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out'
          }}
        >
          <ShieldCheck size={18} color="var(--accent-cyan-light)" />
          {googleLoading ? 'Connecting Google OAuth...' : 'Continue with Google'}
        </button>

        <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Don't have an account? <Link to="/register" style={{ color: 'var(--accent-cyan-light)', textDecoration: 'none', fontWeight: 600 }}>Create an account</Link>
        </p>
      </div>
    </div>
  )
}

export default Login
