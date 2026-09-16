import React, { useState } from 'react'
import { Building2, Handshake, Users, Mail, Check, Plus } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { collaborators } from '../services/mockData'

function Collaborations() {
  const [invited, setInvited] = useState({})

  const toggleInvite = (id) => setInvited((prev) => ({ ...prev, [id]: !prev[id] }))

  const fitTone = (score) =>
    score >= 90 ? { bg: 'rgba(16,185,129,0.12)', color: 'var(--accent-emerald)' }
    : score >= 85 ? { bg: 'rgba(6,182,212,0.12)', color: 'var(--accent-cyan-light)' }
    : { bg: 'rgba(139,92,246,0.12)', color: 'var(--accent-violet)' }

  return (
    <AppLayout
      title="Collaborations"
      subtitle="AI-suggested research partners ranked by topic overlap and network impact."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', width: '100%', margin: '0 auto' }}>

        <section className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem', background: 'linear-gradient(145deg, rgba(6,182,212,0.08) 0%, rgba(139,92,246,0.08) 100%)' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: 'rgba(6,182,212,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Handshake size={22} color="var(--accent-cyan)" />
          </div>
          <div style={{ flexGrow: 1 }}>
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Recommendation Engine</h4>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Collaboration fit blends publication co-authorship density, domain overlap, and geographic complementarity. Top decile partners score ≥90.
            </p>
          </div>
          <Users size={22} color="var(--accent-violet)" style={{ flexShrink: 0 }} />
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {collaborators.map((c) => {
            const tone = fitTone(c.score)
            const isInvited = invited[c.id]
            return (
              <div key={c.id} className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
                  <div style={{ width: '46px', height: '46px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-violet) 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.05rem', color: '#FFFFFF', flexShrink: 0 }}>
                    {c.name.replace('Prof. ', '').replace('Dr. ', '').split(' ').map((w) => w[0]).slice(0, 2).join('')}
                  </div>
                  <div style={{ flexGrow: 1 }}>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{c.name}</h4>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.2rem' }}>
                      <Building2 size={13} color="var(--text-muted)" />
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{c.institution}</span>
                    </div>
                  </div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 800, padding: '0.25rem 0.6rem', borderRadius: '9999px', background: tone.bg, color: tone.color, whiteSpace: 'nowrap' }}>{c.score}%</span>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {c.topics.map((t, i) => (
                    <span key={i} style={{ fontSize: '0.72rem', fontWeight: 600, padding: '0.22rem 0.6rem', borderRadius: '9999px', background: 'rgba(139,92,246,0.12)', color: 'var(--accent-violet)' }}>{t}</span>
                  ))}
                </div>
                <button
                  onClick={() => toggleInvite(c.id)}
                  className={isInvited ? 'btn-secondary' : 'btn-ai-primary'}
                  style={{ marginTop: 'auto', padding: '0.5rem 0.9rem', fontSize: '0.8rem', borderRadius: '9px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.45rem' }}
                >
                  {isInvited ? <><Check size={15} /> Invitation Sent</> : <><Plus size={15} /> Invite to Collaborate</>}
                </button>
              </div>
            )
          })}
        </section>

        <section className="glass-card" style={{ padding: '1.2rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', borderLeft: '3px solid var(--accent-cyan)' }}>
          <Mail size={18} color="var(--accent-cyan)" />
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Collaboration invitations are queued and reviewed by the partner team. Track status and impact in your monthly Innovation Brief.
          </p>
        </section>
      </div>
    </AppLayout>
  )
}

export default Collaborations