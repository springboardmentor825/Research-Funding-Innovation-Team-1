import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Sparkles, 
  Search, 
  User, 
  BookOpen, 
  Award, 
  Lightbulb, 
  Bot,
  Menu,
  X
} from 'lucide-react'

function Sidebar({ mobileOpen, setMobileOpen }) {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Recommendations', path: '/recommendations', icon: Sparkles, badge: 'AI' },
    { label: 'Funding Opportunities', path: '/funding', icon: Search },
    { label: 'My Profile', path: '/profile', icon: User },
    { label: 'Publications', path: '/publications', icon: BookOpen },
    { label: 'Patents', path: '/patents', icon: Award },
    { label: 'Innovation Hub', path: '/innovation', icon: Lightbulb },
  ]

  return (
    <>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div 
          onClick={() => setMobileOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(8, 12, 20, 0.8)',
            backdropFilter: 'blur(4px)',
            zIndex: 40
          }}
        />
      )}

      {/* Sidebar Container */}
      <aside 
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 50,
          transition: 'transform 0.3s ease',
          transform: mobileOpen ? 'translateX(0)' : 'translateX(0)', // responsive handled via media queries
        }}
        className="sidebar-responsive"
      >
        {/* Brand Header */}
        <div style={{
          padding: '1.5rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--border-color)'
        }}>
          <Link to="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
            }}>
              <Sparkles size={22} color="#FFFFFF" />
            </div>
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#F8FAFC', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                AI Fund
              </div>
              <div style={{ fontSize: '0.725rem', color: 'var(--accent-cyan-light)', fontWeight: 500 }}>
                Intelligence Platform
              </div>
            </div>
          </Link>

          <button 
            onClick={() => setMobileOpen(false)}
            style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', display: 'none' }}
            className="mobile-close-btn"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav style={{ padding: '1.25rem 0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem', flexGrow: 1, overflowY: 'auto' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', padding: '0.5rem 0.75rem' }}>
            Main Menu
          </div>

          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen && setMobileOpen(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  padding: '0.75rem 1rem',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  fontWeight: active ? 600 : 500,
                  color: active ? '#F8FAFC' : 'var(--text-secondary)',
                  background: active 
                    ? 'linear-gradient(90deg, rgba(6, 182, 212, 0.18) 0%, rgba(6, 182, 212, 0.05) 100%)' 
                    : 'transparent',
                  borderLeft: active ? '3px solid var(--accent-cyan)' : '3px solid transparent',
                  transition: 'all 0.2s ease',
                  position: 'relative'
                }}
              >
                <Icon size={18} color={active ? 'var(--accent-cyan-light)' : '#94A3B8'} />
                <span style={{ flexGrow: 1 }}>{item.label}</span>
                {item.badge && (
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    padding: '0.15rem 0.45rem',
                    borderRadius: '9999px',
                    background: 'rgba(6, 182, 212, 0.2)',
                    color: 'var(--accent-cyan-light)',
                    border: '1px solid rgba(6, 182, 212, 0.4)'
                  }}>
                    {item.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer info badge */}
        <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', background: 'rgba(15, 23, 42, 0.6)' }}>
          <div style={{
            padding: '0.85rem',
            borderRadius: '10px',
            background: 'rgba(30, 41, 59, 0.6)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: 'var(--accent-emerald)',
              boxShadow: '0 0 8px var(--accent-emerald)'
            }} />
            <div style={{ fontSize: '0.8rem', color: '#E2E8F0', fontWeight: 500 }}>
              AI Engine Online
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
