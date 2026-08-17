import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import authService from '../services/auth'
import { Sparkles, User, Mail, Lock, Shield, ArrowRight } from 'lucide-react'

function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('researcher')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginBottom: '1.5rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
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
          Create Account
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
          Join the research funding & intelligence network.
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

        {success && (
          <div style={{
            padding: '0.75rem 1rem',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#34D399',
            fontSize: '0.85rem',
            marginBottom: '1.25rem'
          }}>
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.15rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Full Name
            </label>
            <div style={{ position: 'relative' }}>
              <User size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input 
                className="ai-input" 
                type="text" 
                value={fullName} 
                onChange={e => setFullName(e.target.value)} 
                required 
                placeholder="Dr. Jane Doe" 
                style={{ paddingLeft: '2.5rem' }}
              />
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
                placeholder="researcher@university.edu" 
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

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Account Role
            </label>
            <div style={{ position: 'relative' }}>
              <Shield size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', zIndex: 1 }} />
              <select className="ai-select" value={role} onChange={e => setRole(e.target.value)} style={{ paddingLeft: '2.5rem' }}>
                <option value="researcher">Researcher / Innovator</option>
                <option value="funder">Investor / Funder</option>
                <option value="admin">Administrator</option>
              </select>
            </div>
          </div>

          <button 
            className="btn-ai-primary" 
            type="submit" 
            disabled={loading} 
            style={{ marginTop: '0.5rem', width: '100%', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        <p style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-cyan-light)', textDecoration: 'none', fontWeight: 600 }}>Log in here</Link>
        </p>
      </div>
    </div>
  )
}

export default Register
