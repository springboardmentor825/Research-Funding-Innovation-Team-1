import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Sparkles, UserCheck, Rocket, Briefcase, GraduationCap, ArrowRight } from 'lucide-react'

function GoogleRoleSelection() {
  const [selectedRole, setSelectedRole] = useState('startup_founder')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { pendingToken, completeGoogleRegistration } = useAuth()
  const navigate = useNavigate()

  const handleComplete = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await completeGoogleRegistration(pendingToken, selectedRole)
      if (res.status === 'success' && res.user) {
        switch (res.user.role) {
          case 'startup_founder':
            navigate('/startup/dashboard')
            break
          case 'researcher':
          default:
            navigate('/dashboard')
            break
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete role selection. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const roleCards = [
    {
      id: 'researcher',
      title: 'Researcher',
      icon: GraduationCap,
      description: 'Access grant opportunities, publication analytics, and AI research recommendations.'
    },
    {
      id: 'startup_founder',
      title: 'Startup Founder',
      icon: Rocket,
      description: 'Explore funding opportunities, commercialization pathways, and patent insights.'
    }
  ]

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
          maxWidth: '560px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid var(--border-glow)'
        }}
      >
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
              Welcome to AI Fund Platform
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)', fontWeight: 500 }}>
              Google Account Verified
            </span>
          </div>
        </div>

        <h3 style={{ fontSize: '1.25rem', color: '#F8FAFC', fontWeight: 700, marginBottom: '0.35rem' }}>
          Select Your Role to Continue
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
          Please choose your primary platform role to customize your workspace dashboard.
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

        <form onSubmit={handleComplete} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {roleCards.map(card => {
              const IconComp = card.icon
              const isSelected = selectedRole === card.id
              return (
                <div
                  key={card.id}
                  onClick={() => setSelectedRole(card.id)}
                  style={{
                    padding: '1.15rem',
                    borderRadius: '12px',
                    border: isSelected ? '2px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
                    backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.1)' : '#1E293B',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '10px',
                    backgroundColor: isSelected ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <IconComp size={20} color={isSelected ? '#0F172A' : 'var(--accent-cyan-light)'} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: '0 0 0.25rem 0' }}>
                      {card.title}
                    </h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.3 }}>
                      {card.description}
                    </p>
                  </div>
                  {isSelected && (
                    <UserCheck size={20} color="var(--accent-cyan)" />
                  )}
                </div>
              )
            })}
          </div>

          <button
            className="btn-ai-primary"
            type="submit"
            disabled={loading}
            style={{ marginTop: '1rem', width: '100%', opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Activating Account...' : 'Complete Setup & Continue'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>
      </div>
    </div>
  )
}

export default GoogleRoleSelection
