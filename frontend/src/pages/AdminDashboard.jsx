import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ShieldCheck, Users, Briefcase, FileText, Activity, Server, CircleDollarSign, UserPlus, Send, MapPin } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { useAuth } from '../context/AuthContext'
import adminService from '../services/admin'
import analyticsService from '../services/analytics'

const fmt = (n) => (n === null || n === undefined || isNaN(n) ? '—' : Number(n).toLocaleString())

const roleColors = {
  admin: { bg: 'rgba(239, 68, 68, 0.15)', fg: '#f87171' },
  funder: { bg: 'rgba(245, 158, 11, 0.15)', fg: '#fbbf24' },
  researcher: { bg: 'rgba(139, 92, 246, 0.18)', fg: '#c4b5fd' }
}

const statusColors = {
  submitted: { bg: 'rgba(6, 182, 212, 0.15)', fg: '#67e8f9' },
  withdrawn: { bg: 'rgba(148, 163, 184, 0.15)', fg: '#94a3b8' }
}

function AdminStat({ icon: Icon, label, value, tint }) {
  return (
    <div className="glass-card" style={{ padding: '1.25rem 1.4rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{
        width: '44px', height: '44px', borderRadius: '12px', flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: `${tint}22`, border: `1px solid ${tint}44`, color: tint
      }}>
        <Icon size={20} />
      </div>
      <div style={{ minWidth: 0 }}>
        <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>{label}</p>
        <p style={{ margin: '0.15rem 0 0 0', fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.1 }}>{value}</p>
      </div>
    </div>
  )
}

function AdminDashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [corpus, setCorpus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const [overview, corpusStats] = await Promise.all([
          adminService.getOverview(),
          analyticsService.overview().catch(() => null)
        ])
        if (!mounted) return
        setData(overview)
        setCorpus(corpusStats)
      } catch (err) {
        if (mounted) setError(err.response?.data?.detail || 'Could not load platform data.')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  const uc = data?.user_counts || {}
  const ac = data?.application_counts || {}

  return (
    <AppLayout
      title="Platform Command Center"
      subtitle={`Administration console — ${user?.full_name || 'Administrator'}`}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem', maxWidth: '1240px', width: '100%', margin: '0 auto' }}>

        {/* System banner */}
        <section className="glass-card" style={{ padding: '1.75rem 2rem', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1.25rem', background: 'linear-gradient(120deg, rgba(139,92,246,0.14) 0%, rgba(239,68,68,0.08) 55%, rgba(17,24,39,0.4) 100%)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '52px', height: '52px', borderRadius: '14px', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'linear-gradient(135deg, var(--accent-violet) 0%, #dc2626 100%)',
              boxShadow: '0 0 20px rgba(139, 92, 246, 0.35)'
            }}>
              <ShieldCheck size={26} color="#fff" />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                Platform Command Center
              </h2>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Oversight, user accounts, and grant activity across Infera.
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>● SYSTEMS ONLINE</span>
            <span className="badge" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd', textTransform: 'none' }}>ROLE: ADMIN</span>
          </div>
        </section>

        {error && (
          <div style={{ padding: '1rem', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.12)', color: '#fca5a5', fontSize: '0.9rem', fontWeight: 500 }}>
            {error}
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <Server size={28} style={{ marginBottom: '0.6rem', opacity: 0.5 }} />
            <p style={{ margin: 0 }}>Loading platform telemetry…</p>
          </div>
        ) : (
          <>
            {/* KPI stat rail */}
            <section className="glass-card" style={{ padding: '1.5rem' }}>
              <header style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.1rem' }}>
                <Activity size={17} color="var(--accent-violet)" />
                <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Platform Telemetry</h3>
              </header>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                <AdminStat icon={Users} label="Registered Users" value={fmt(uc.total) ?? '…'} tint="#8b5cf6" />
                <AdminStat icon={UserPlus} label="Researchers" value={fmt(uc.researcher) ?? '…'} tint="#8b5cf6" />
                <AdminStat icon={CircleDollarSign} label="Funders" value={fmt(uc.funder) ?? '…'} tint="#f59e0b" />
                <AdminStat icon={ShieldCheck} label="Admins" value={fmt(uc.admin) ?? '…'} tint="#ef4444" />
                <AdminStat icon={FileText} label="Grant Applications" value={fmt(ac.total) ?? '…'} tint="#06b6d4" />
                <AdminStat icon={Briefcase} label="Open Funding" value={fmt(data.open_funding) ?? '…'} tint="#10b981" />
                <AdminStat icon={MapPin} label="Corpus (publications)" value={fmt(corpus?.total_publications) ?? '…'} tint="#3b82f6" />
              </div>
            </section>

            {/* Recent users + applications */}
            <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.5rem' }}>
              <div className="glass-card" style={{ padding: '1.5rem', minWidth: 0 }}>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--accent-violet)' }}>Recently Registered Users</h3>
                    <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Newest accounts on the platform</p>
                  </div>
                  <Link to="/settings" className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem' }}>Manage</Link>
                </header>
                {data.recent_users?.length ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem', overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                      <thead>
                        <tr style={{ color: 'var(--text-muted)', textAlign: 'left' }}>
                          <th style={{ padding: '0.4rem 0.6rem', fontWeight: 600 }}>User</th>
                          <th style={{ padding: '0.4rem 0.6rem', fontWeight: 600 }}>Role</th>
                          <th style={{ padding: '0.4rem 0.6rem', fontWeight: 600 }}>Login</th>
                          <th style={{ padding: '0.4rem 0.6rem', fontWeight: 600 }}>Joined</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.recent_users.map((u) => {
                          const rc = roleColors[u.role] || roleColors.researcher
                          return (
                            <tr key={u.id} style={{ borderTop: '1px solid var(--border-color)' }}>
                              <td style={{ padding: '0.55rem 0.6rem' }}>
                                <div style={{ fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '180px' }}>{u.full_name || '—'}</div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{u.email}</div>
                              </td>
                              <td style={{ padding: '0.55rem 0.6rem' }}>
                                <span className="badge" style={{ background: rc.bg, color: rc.fg, textTransform: 'capitalize' }}>{u.role}</span>
                              </td>
                              <td style={{ padding: '0.55rem 0.6rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{u.login_type}</td>
                              <td style={{ padding: '0.55rem 0.6rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                                {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No users yet.</p>
                )}
              </div>

              <div className="glass-card" style={{ padding: '1.5rem', minWidth: 0 }}>
                <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>Recent Grant Applications</h3>
                    <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Latest submissions across teams</p>
                  </div>
                  <Link to="/funding" className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem' }}>Funding</Link>
                </header>
                {data.recent_applications?.length ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                    {data.recent_applications.map((a) => {
                      const sc = statusColors[a.status] || roleColors.researcher
                      return (
                        <div key={a.id} style={{ padding: '0.8rem 1rem', borderRadius: 10, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
                            <div style={{ minWidth: 0 }}>
                              <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.87rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.title}</div>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                                <Send size={11} style={{ verticalAlign: '-2px', marginRight: '0.25rem' }} />
                                {a.applicant_name} · {a.applicant_email}
                              </div>
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>{a.funder} · {a.amount_range}</div>
                            </div>
                            <span className="badge" style={{ background: sc.bg, color: sc.fg, whiteSpace: 'nowrap', textTransform: 'capitalize' }}>{a.status}</span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No applications submitted yet.</p>
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </AppLayout>
  )
}

export default AdminDashboard