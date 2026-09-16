import React, { useState } from 'react'
import { Microscope, Cpu, FlaskConical, Gauge, CalendarPlus, MapPin, Check } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { resources } from '../services/mockData'

const typeIcon = {
  Imaging: Microscope,
  Computing: Cpu,
  Fabrication: FlaskConical,
  Measurement: Gauge,
  'Lab Space': Microscope,
}

const statusTone = {
  available: { bg: 'rgba(16,185,129,0.12)', color: 'var(--accent-emerald)', label: 'Available' },
  'in-use': { bg: 'rgba(245,158,11,0.12)', color: '#F59E0B', label: 'In Use' },
  maintenance: { bg: 'rgba(239,68,68,0.12)', color: '#EF4444', label: 'Maintenance' },
}

function LabResources() {
  const [booked, setBooked] = useState({})

  const toggleBook = (id) => setBooked((prev) => ({ ...prev, [id]: !prev[id] }))

  return (
    <AppLayout
      title="Lab Resources"
      subtitle="Shared research equipment and lab space — check availability and book on demand."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', width: '100%', margin: '0 auto' }}>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {resources.map((r) => {
            const Icon = typeIcon[r.type] || FlaskConical
            const st = statusTone[r.status] || statusTone.available
            const isBooked = booked[r.id]
            const canBook = r.status === 'available'
            return (
              <div key={r.id} className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '0.75rem' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(6,182,212,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={20} color="var(--accent-cyan)" />
                  </div>
                  <span style={{ fontSize: '0.7rem', fontWeight: 700, padding: '0.25rem 0.6rem', borderRadius: '9999px', background: st.bg, color: st.color, whiteSpace: 'nowrap' }}>{st.label}</span>
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{r.name}</h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.3rem' }}>
                    <MapPin size={13} color="var(--text-muted)" />
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{r.location}</span>
                  </div>
                </div>
                <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
                  <button
                    onClick={() => canBook && toggleBook(r.id)}
                    disabled={!canBook}
                    className={isBooked ? 'btn-secondary' : 'btn-ai-primary'}
                    style={{ width: '100%', padding: '0.5rem 0.9rem', fontSize: '0.8rem', borderRadius: '9px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.45rem', opacity: canBook ? 1 : 0.4, cursor: canBook ? 'pointer' : 'not-allowed' }}
                  >
                    {isBooked ? <><Check size={15} /> Booked</> : <><CalendarPlus size={15} /> {canBook ? 'Book Resource' : 'Currently Unavailable'}</>}
                  </button>
                </div>
              </div>
            )
          })}
        </section>

        <section className="glass-card" style={{ padding: '1.2rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem', borderLeft: '3px solid var(--accent-emerald)' }}>
          <Check size={18} color="var(--accent-emerald)" />
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Bookings request a timeslot confirmation from the lab administrator. Maintenance and in-use equipment auto-approval is disabled to avoid conflicts.
          </p>
        </section>
      </div>
    </AppLayout>
  )
}

export default LabResources