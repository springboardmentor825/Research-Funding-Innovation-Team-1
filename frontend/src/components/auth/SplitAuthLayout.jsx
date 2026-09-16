import React from 'react'
import { ArrowRight, Database, Sparkles, Bot, Target, ShieldCheck } from 'lucide-react'

const features = [
  { icon: Target, title: 'Personalized funding matches', desc: 'Ranked opportunities scored against your research profile.' },
  { icon: Database, title: '50k research corpus', desc: 'Live analytics across a global scholarly publication corpus.' },
  { icon: Bot, title: 'AI research assistant', desc: 'Ask anything — get sourced answers with citations.' },
  { icon: ShieldCheck, title: 'Innovation intelligence', desc: 'Patent landscapes, IP tracking, and collaboration tools.' }
]

const stats = [
  { value: '50K+', label: 'Publications' },
  { value: '40+', label: 'Funding tracks' },
  { value: '3', label: 'Workstreams' }
]

function LogoMark({ size = 38 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="inferaGrad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
          <stop stopColor="#06B6D4" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
      </defs>
      <path d="M24 2 44 12v14c0 10-8 18-20 20C12 44 4 36 4 26V12L24 2Z" fill="url(#inferaGrad)" fillOpacity="0.18" stroke="url(#inferaGrad)" strokeWidth="2.5" strokeLinejoin="round" />
      <path d="M24 14 32 20.5v8L24 35l-8-6.5v-8L24 14Z" stroke="url(#inferaGrad)" strokeWidth="2" strokeLinejoin="round" fill="url(#inferaGrad)" fillOpacity="0.25" />
      <circle cx="24" cy="24" r="2.6" fill="#E0F2FE" />
    </svg>
  )
}

function SplitAuthLayout({ children, head, foot }) {
  return (
    <div className="auth-split">
      <section className="auth-brand">
        <div className="auth-brand-glow auth-brand-glow-a" />
        <div className="auth-brand-glow auth-brand-glow-b" />

        <div className="auth-brand-inner">
          <div className="auth-brand-logo">
            <LogoMark />
            <span className="auth-brand-wordmark">INFERA</span>
          </div>

          <h1 className="auth-brand-title" style={{ fontSize: '2.05rem' }}>
            Research Intelligence,<br />
            <span style={{ background: 'linear-gradient(90deg, var(--accent-cyan-light) 0%, #a78bfa 60%, var(--accent-cyan) 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>
              Funding &amp; Innovation Hub
            </span>
          </h1>
          <p className="auth-brand-desc">
            Discover open grant schemes, track your IP, score your innovation readiness, and collaborate — all in one AI-powered workspace.
          </p>

          <ul className="auth-brand-features">
            {features.map((f) => (
              <li key={f.title}>
                <span className="auth-feature-icon"><f.icon size={18} /></span>
                <span className="auth-feature-text">
                  <strong>{f.title}</strong>
                  <small>{f.desc}</small>
                </span>
              </li>
            ))}
          </ul>

          <div className="auth-brand-stats">
            {stats.map((s) => (
              <div key={s.label}>
                <strong>{s.value}</strong>
                <span>{s.label}</span>
              </div>
            ))}
          </div>

          <p className="auth-brand-note">
            <Sparkles size={13} /> Built for teams, backed by OpenAlex data and an AI research assistant.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-panel-inner">
          <div className="auth-mobile-brand">
            <LogoMark size={30} />
            <span className="auth-brand-wordmark">INFERA</span>
          </div>
          {head}
          {children}
          {foot}
        </div>
      </section>
    </div>
  )
}

export default SplitAuthLayout