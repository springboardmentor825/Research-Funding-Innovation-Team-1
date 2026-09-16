import React, { useState } from 'react'
import { BellRing, BadgeDollarSign, BookOpenCheck, FlaskConical, Users, CheckCheck, ShieldAlert } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { alerts } from '../services/mockData'

const typeConfig = {
  patent: { icon: FlaskConical, color: 'var(--accent-cyan)' },
  grant: { icon: BadgeDollarSign, color: 'var(--accent-emerald)' },
  citation: { icon: BookOpenCheck, color: 'var(--accent-violet)' },
  system: { icon: ShieldAlert, color: 'var(--text-secondary)' },
  collab: { icon: Users, color: '#F59E0B' },
}

function Alerts() {
  const [items, setItems] = useState(alerts)

  const markRead = (id) => setItems((prev) => prev.map((a) => (a.id === id ? { ...a, read: true } : a)))
  const markAllRead = () => setItems((prev) => prev.map((a) => ({ ...a, read: true })))

  const unread = items.filter((a) => !a.read)
  const read = items.filter((a) => a.read)
  const unreadCount = unread.length

  return (
    <AppLayout
      title="Alerts & Notifications"
      subtitle={`${unreadCount} unread ${unreadCount === 1 ? 'alert' : 'alerts'} across your portfolio, grants, citations, and collaborations.`}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', width: '100%', margin: '0 auto' }}>

        {unreadCount > 0 && (
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button onClick={markAllRead} className="btn-ai-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', borderRadius: '9px', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <CheckCheck size={15} /> Mark all as read
            </button>
          </div>
        )}

        {unread.length > 0 && (
          <section>
            <h3 style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--accent-cyan-light)', margin: '0 0 0.85rem 0' }}>New ({unread.length})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {unread.map((a) => {
                const cfg = typeConfig[a.type] || typeConfig.system
                const Icon = cfg.icon
                return (
                  <div key={a.id} className="glass-card" style={{ padding: '1.1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.9rem', borderLeft: `3px solid ${cfg.color}` }}>
                    <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(139,92,246,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon size={18} color={cfg.color} />
                    </div>
                    <div style={{ flexGrow: 1 }}>
                      <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-primary)' }}>{a.message}</p>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{a.time} · {a.type.toUpperCase()}</span>
                    </div>
                    <button onClick={() => markRead(a.id)} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', borderRadius: '8px', whiteSpace: 'nowrap' }}>Mark read</button>
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {read.length > 0 && (
          <section>
            <h3 style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: 'var(--text-muted)', margin: '0 0 0.85rem 0' }}>Earlier ({read.length})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {read.map((a) => {
                const cfg = typeConfig[a.type] || typeConfig.system
                const Icon = cfg.icon
                return (
                  <div key={a.id} className="glass-card" style={{ padding: '0.9rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.9rem', opacity: 0.65 }}>
                    <div style={{ width: '34px', height: '34px', borderRadius: '9px', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Icon size={16} color={cfg.color} />
                    </div>
                    <div style={{ flexGrow: 1 }}>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{a.message}</p>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{a.time} · {a.type.toUpperCase()}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {unreadCount === 0 && read.length === 0 && (
          <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <BellRing size={28} style={{ marginBottom: '0.5rem', opacity: 0.5 }} />
            <p style={{ margin: 0 }}>No notifications yet.</p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default Alerts