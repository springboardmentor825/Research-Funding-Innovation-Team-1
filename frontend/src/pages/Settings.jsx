import React, { useState, useEffect } from 'react'
import { Link2, Download, Save, Bell, Database } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { useAuth } from '../context/AuthContext'

function Toggle({ label, hint, checked, onChange }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.6rem 0' }}>
      <div style={{ flexGrow: 1 }}>
        <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>{label}</div>
        {hint ? <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{hint}</div> : null}
      </div>
      <button
        onClick={() => onChange(!checked)}
        style={{
          width: '42px', height: '23px', borderRadius: '9999px', border: 'none', cursor: 'pointer', position: 'relative',
          background: checked ? 'linear-gradient(90deg, var(--accent-cyan), var(--accent-violet))' : 'rgba(255,255,255,0.12)',
          transition: 'background 0.2s ease'
        }}
        aria-pressed={checked}
      >
        <span style={{ position: 'absolute', top: '2.5px', left: checked ? '21px' : '3px', width: '18px', height: '18px', borderRadius: '50%', background: '#FFFFFF', transition: 'left 0.2s ease', boxShadow: '0 2px 6px rgba(0,0,0,0.3)' }} />
      </button>
    </div>
  )
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>{label}</label>
      <input
        className="input-field"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{ width: '100%', padding: '0.6rem 0.85rem', borderRadius: '9px', fontSize: '0.88rem' }}
      />
    </div>
  )
}

function Settings() {
  const { user } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [affiliation, setAffiliation] = useState('')
  const [saved, setSaved] = useState(false)
  const [prefs, setPrefs] = useState({ deadlines: true, patents: false, citations: true, reports: false })

  useEffect(() => {
    if (user) {
      setName(user.full_name || user.name || '')
      setEmail(user.email || '')
      setAffiliation(user.organization || user.profile?.organization || '')
    }
  }, [user])

  const togglePref = (key) => () => setPrefs((prev) => ({ ...prev, [key]: !prev[key] }))
  const handleSave = (e) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const exportData = () => {
    const blob = new Blob([JSON.stringify({ profile: { name, email, affiliation }, preferences: prefs, dataSources, connected }, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'infera_export.json'; a.click()
    URL.revokeObjectURL(url)
  }

  const dataSources = [
    { name: 'ORCID', linked: true },
    { name: 'Scopus', linked: true },
    { name: 'USPTO + EPO Patents', linked: false },
    { name: 'Dimensions', linked: false },
  ]
  const connected = [
    { name: 'Google Scholar', linked: true },
    { name: 'OpenAlex', linked: true },
    { name: 'LinkedIn', linked: false },
  ]

  return (
    <AppLayout
      title="Settings"
      subtitle="Manage your profile, notification preferences, and connected research data sources."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1000px', width: '100%', margin: '0 auto' }}>

        <form className="glass-card" style={{ padding: '1.5rem' }} onSubmit={handleSave}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
            <Save size={19} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Profile Settings</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <Field label="Display Name" value={name} onChange={setName} placeholder="Your full name" />
            <Field label="Email" value={email} onChange={setEmail} placeholder="you@example.com" />
            <Field label="Affiliation" value={affiliation} onChange={setAffiliation} placeholder="Organization / university" />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', marginTop: '1.25rem' }}>
            <button type="submit" className="btn-ai-primary" style={{ padding: '0.55rem 1.15rem', fontSize: '0.85rem', borderRadius: '9px', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Save size={15} /> Save Changes
            </button>
            {saved && <span style={{ fontSize: '0.82rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>✓ Settings saved</span>}
          </div>
        </form>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <section className="glass-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
              <Bell size={19} color="var(--accent-violet)" />
              <h3 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Notification Preferences</h3>
            </div>
            <Toggle label="Funding deadlines" hint="Reminders before grant deadlines" checked={prefs.deadlines} onChange={togglePref('deadlines')} />
            <Toggle label="Patent milestones" hint="Examination & filing updates" checked={prefs.patents} onChange={togglePref('patents')} />
            <Toggle label="Citation thresholds" hint="When a paper crosses citation milestones" checked={prefs.citations} onChange={togglePref('citations')} />
            <Toggle label="Reports" hint="When monthly briefs are ready" checked={prefs.reports} onChange={togglePref('reports')} />
          </section>

          <section className="glass-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
              <Database size={19} color="var(--accent-emerald)" />
              <h3 style={{ fontSize: '1.05rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Data Sources</h3>
            </div>
            {dataSources.map((d) => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: '0.86rem', color: 'var(--text-primary)' }}>{d.name}</span>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '0.2rem 0.55rem', borderRadius: '9999px', background: d.linked ? 'rgba(16,185,129,0.12)' : 'rgba(148,163,184,0.12)', color: d.linked ? 'var(--accent-emerald)' : 'var(--text-muted)' }}>
                  {d.linked ? 'Linked' : 'Not linked'}
                </span>
              </div>
            ))}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', margin: '1rem 0 0.5rem 0' }}>
              <Link2 size={17} color="var(--accent-cyan)" />
              <h4 style={{ fontSize: '0.92rem', margin: 0, fontWeight: 700, color: 'var(--text-primary)' }}>Connected Accounts</h4>
            </div>
            {connected.map((c) => (
              <div key={c.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0' }}>
                <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>{c.name}</span>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, padding: '0.18rem 0.5rem', borderRadius: '9999px', background: c.linked ? 'rgba(16,185,129,0.12)' : 'rgba(148,163,184,0.12)', color: c.linked ? 'var(--accent-emerald)' : 'var(--text-muted)' }}>
                  {c.linked ? 'Linked' : 'Link'}
                </span>
              </div>
            ))}
          </section>
        </div>

        <section className="glass-card" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ flexGrow: 1 }}>
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Export Data</h4>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Download your profile, preferences, and connector status as a JSON archive.</p>
          </div>
          <button onClick={exportData} className="btn-ai-secondary" style={{ padding: '0.55rem 1.1rem', fontSize: '0.82rem', borderRadius: '9px', display: 'flex', alignItems: 'center', gap: '0.45rem', flexShrink: 0 }}>
            <Download size={15} /> Export
          </button>
        </section>
      </div>
    </AppLayout>
  )
}

export default Settings