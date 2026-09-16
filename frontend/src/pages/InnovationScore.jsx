import React from 'react'
import { Lightbulb, Target, TrendingUp, Users, Trophy } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { scoreBreakdown, benchmarks, improvements } from '../services/mockData'

function ScoreRing({ value, size = 180, stroke = 14 }) {
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--accent-cyan)" />
            <stop offset="100%" stopColor="var(--accent-violet)" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke="url(#ringGrad)" strokeWidth={stroke} fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease', filter: 'drop-shadow(0 0 8px rgba(6,182,212,0.4))' }}
        />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontSize: '2.75rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>{value}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>/ 100</div>
      </div>
    </div>
  )
}

function ProgressBar({ value, target }) {
  const onTrack = value >= target
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ flexGrow: 1, height: '8px', borderRadius: '9999px', backgroundColor: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
        <div
          style={{
            width: `${Math.min(value, 100)}%`,
            height: '100%',
            borderRadius: '9999px',
            background: onTrack ? 'linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald))' : 'linear-gradient(90deg, var(--accent-violet), var(--accent-cyan))',
            transition: 'width 0.6s ease',
            boxShadow: `0 0 10px ${onTrack ? 'rgba(16,185,129,0.35)' : 'rgba(6,182,212,0.3)'}`
          }}
        />
      </div>
      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', minWidth: '2rem', textAlign: 'right' }}>{value}</span>
    </div>
  )
}

function InnovationScore() {
  const overall = 78

  return (
    <AppLayout
      title="Innovation Score"
      subtitle="A composite AI measure of your research novelty, translation, velocity, collaboration, and funding efficiency."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', width: '100%', margin: '0 auto' }}>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem', alignItems: 'start' }}>
          <div className="glass-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', background: 'linear-gradient(145deg, rgba(6,182,212,0.08) 0%, rgba(139,92,246,0.08) 100%)' }}>
            <ScoreRing value={overall} />
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-cyan-light)' }}>Portfolio Innovation Health</div>
          </div>

          <div className="glass-card" style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
            {benchmarks.map((b) => (
              <div key={b.label} style={{ padding: '0.9rem', borderRadius: '12px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{b.label}</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: b.label === 'Your Score' ? 'var(--accent-cyan-light)' : 'var(--text-primary)', marginTop: '0.25rem' }}>{b.value}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
            <Target size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Metric Breakdown</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>
            {scoreBreakdown.map((m) => (
              <div key={m.label}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{m.label}</span>
                  <span style={{ fontSize: '0.7rem', color: m.value >= m.target ? 'var(--accent-emerald)' : 'var(--text-muted)', fontWeight: 600 }}>
                    {m.value >= m.target ? '● On track' : `● Target ${m.target}`}
                  </span>
                </div>
                <ProgressBar value={m.value} target={m.target} />
                <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.78rem', color: 'var(--text-muted)' }}>{m.hint}</p>
              </div>
            ))}
          </div>
        </section>

        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <Lightbulb size={20} color="var(--accent-violet)" />
              <h3 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Suggested Improvements</h3>
            </div>
            <ol style={{ margin: 0, paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {improvements.map((imp, i) => (
                <li key={i} style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{imp}</li>
              ))}
            </ol>
          </div>

          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <TrendingUp size={20} color="var(--accent-emerald)" />
              <h3 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Score Drivers</h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {scoreBreakdown.slice(0, 3).map((m) => (
                <div key={m.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 0.9rem', borderRadius: '10px', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
                    {m.label === 'Novelty' ? <Users size={16} color="var(--accent-cyan)" /> : m.label === 'Translation' ? <Trophy size={16} color="var(--accent-violet)" /> : <Target size={16} color="var(--accent-emerald)" />}
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{m.label}</span>
                  </div>
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{m.value}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}

export default InnovationScore