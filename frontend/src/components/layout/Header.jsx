import React from 'react'
import { useAuth } from '../../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Search, Bell, LogOut, User as UserIcon, Menu } from 'lucide-react'

function Header({ title, subtitle, onSearchChange, searchValue, setMobileOpen }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Extract user initials
  const initials = user?.full_name 
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'R'

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '1.25rem 2rem',
      backgroundColor: 'rgba(8, 12, 20, 0.75)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      {/* Title & Subtitle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button 
          onClick={() => setMobileOpen && setMobileOpen(true)}
          style={{
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid var(--border-color)',
            color: '#F8FAFC',
            padding: '0.5rem',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'none'
          }}
          className="mobile-menu-btn"
        >
          <Menu size={20} />
        </button>

        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#F8FAFC', margin: 0, letterSpacing: '-0.02em' }}>
            {title || 'Funding Recommendations'}
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
            {subtitle || 'Personalized for you based on your research profile'}
          </p>
        </div>
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Global Search Bar */}
        <div style={{ position: 'relative', width: '240px' }} className="header-search">
          <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Search opportunities..."
            value={searchValue || ''}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
            className="ai-input"
            style={{ paddingLeft: '2.5rem', fontSize: '0.85rem', height: '38px' }}
          />
        </div>

        {/* Notification Icon */}
        <button 
          style={{
            position: 'relative',
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid var(--border-color)',
            color: '#94A3B8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
          title="Notifications"
        >
          <Bell size={18} />
          <span style={{
            position: 'absolute',
            top: '6px',
            right: '6px',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-cyan)'
          }} />
        </button>

        {/* User Profile Info & Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingLeft: '0.5rem', borderLeft: '1px solid var(--border-color)' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-violet) 100%)',
            color: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '0.9rem',
            boxShadow: '0 0 10px rgba(6, 182, 212, 0.3)'
          }}>
            {initials}
          </div>
          
          <div className="header-user-info" style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#F8FAFC', lineHeight: 1.2 }}>
              {user?.full_name || 'Researcher'}
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--accent-cyan-light)', textTransform: 'capitalize' }}>
              {user?.role || 'Researcher'}
            </div>
          </div>

          {/* Logout Action */}
          <button
            onClick={handleLogout}
            style={{
              background: 'none',
              border: 'none',
              color: '#94A3B8',
              cursor: 'pointer',
              marginLeft: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0.35rem',
              borderRadius: '6px',
              transition: 'all 0.2s ease'
            }}
            title="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
