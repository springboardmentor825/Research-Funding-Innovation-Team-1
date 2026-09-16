import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, Briefcase, Target, Layers, CalendarDays, IndianRupee, Building2, Landmark } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import patentAnalyticsService from '../services/patentAnalytics'

const fmt = (n) => (n === null || n === undefined || isNaN(n) ? '0' : Number(n).toLocaleString())

const fitTier = (fit) => {
  if (fit === null || fit === undefined || isNaN(fit)) return { label: 'Newly Open', color: '#94a3b8', bg: 'rgba(148,163,184,0.14)' }
  if (fit >= 70) return { label: 'Strong Fit', color: '#34d399', bg: 'rgba(16,185,129,0.14)' }
  if (fit >= 40) return { label: 'Reviewing', color: '#fbbf24', bg: 'rgba(245,158,11,0.14)' }
  return { label: 'Newly Open', color: '#94a3b8', bg: 'rgba(148,163,184,0.14)' }
}

const toDate = (d) => (d ? new Date(d).toLocaleDateString() : '—')

function FunderDashboard() {
  const { user } = useAuth()
  const [ops, setOps] = useState([])
  const [landscape, setLandscape] = useState(null)
  const [myApps, setMyApps] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const [opportunities, land, apps] = await Promise.all([
          fundingService.searchFunding({}),
          patentAnalyticsService.researchLandscape().catch(() => null),
          fundingService.getApplications()
        ])
        if (!mounted) return
        setOps(opportunities)
        setLandscape(land)
        setMyApps(apps)
      } catch (err) {
        console.error('Failed to load funder data:', err)
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  const strong = ops.filter(o => (o.semantic_fit ?? 0) >= 70)
  const reviewing = ops.filter(o => { const f = o.semantic_fit ?? 0; return f >= 40 && f < 70 })
  const fresh = ops.filter(o => { const f = o.semantic_fit ?? 0; return f < 40 || o.semantic_fit === null })

  const avgFit = ops.length ? Math.round(ops.reduce((s, o) => s + (o.semantic_fit ?? 0), 0) / ops.length) : 0
  const hotSectors = landscape?.hot_domains?.slice(0, 5) || []
  const maxPubs = hotSectors.length ? Math.max(...hotSectors.map(h => h.publication_count), 1) : 1

  const columns = [
    { title: 'Strong Fit', icon: Target, color: '#34d399', items: strong.slice(0, 5), hint: `${strong.length} opportunities` },
    { title: 'Reviewing', icon: TrendingUp, color: '#fbbf24', items: reviewing.slice(0, 5), hint: `${reviewing.length} opportunities` },
    { title: 'Newly Open', icon: Layers, color: '#94a3b8', items: fresh.slice(0, 5), hint: `${fresh.length} opportunities` }
  ]

  return (
    <AppLayout
      title="Investment & Grant Pipeline"
      subtitle={`Deal flow view for ${user?.full_name || 'Startup Founder'}`}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem', maxWidth: '1280px', width: '100%', margin: '0 auto' }}>

        {/* Hero banner */}
        <section className="glass-card" style={{
          padding: '1.75rem 2rem',
          display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1.25rem',
          background: 'linear-gradient(120deg, rgba(16,185,129,0.14) 0%, rgba(245,158,11,0.10) 60%, rgba(17,24,39,0.4) 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '52px', height: '52px', borderRadius: '14px', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'linear-gradient(135deg, var(--accent-emerald) 0%, #f59e0b 100%)',
              boxShadow: '0 0 20px rgba(16, 185, 129, 0.35)'
            }}>
              <Landmark size={26} color="#fff" />
            </div>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                Investment &amp; Grant Pipeline
              </h2>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Track open schemes, sector momentum, and your funding engagement.
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>ROLE: STARTUP FOUNDER</span>
            <Link to="/funding" className="btn-primary" style={{ padding: '0.5rem 1.15rem', fontSize: '0.85rem' }}>
              Explore Funding
            </Link>
          </div>
        </section>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <Briefcase size={28} style={{ marginBottom: '0.6rem', opacity: 0.5 }} />
            <p style={{ margin: 0 }}>Building pipeline…</p>
          </div>
        ) : (
          <>
            {/* KPI row */}
            <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
              <div className="glass-card" style={{ padding: '1.25rem 1.4rem', borderLeft: '3px solid var(--accent-emerald)' }}>
                <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>Open Opportunities</p>
                <p style={{ margin: '0.15rem 0 0 0', fontSize: '1.6rem', fontWeight: 800, color: '#34d399', lineHeight: 1.1 }}>{fmt(ops.length)}</p>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.4rem', borderLeft: '3px solid #f59e0b' }}>
                <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>Avg. Fit Score</p>
                <p style={{ margin: '0.15rem 0 0 0', fontSize: '1.6rem', fontWeight: 800, color: '#fbbf24', lineHeight: 1.1 }}>{avgFit}%</p>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.4rem', borderLeft: '3px solid var(--accent-cyan)' }}>
                <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>Hot Sectors</p>
                <p style={{ margin: '0.15rem 0 0 0', fontSize: '1.6rem', fontWeight: 800, color: '#67e8f9', lineHeight: 1.1 }}>{fmt(hotSectors.length)}</p>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.4rem', borderLeft: '3px solid var(--accent-violet)' }}>
                <p style={{ margin: 0, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>My Engagement</p>
                <p style={{ margin: '0.15rem 0 0 0', fontSize: '1.6rem', fontWeight: 800, color: '#c4b5fd', lineHeight: 1.1 }}>{fmt(myApps.length)}</p>
              </div>
            </section>

            {/* Pipeline kanban */}
            <section style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <header>
                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>Deal Pipeline</h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Opportunities grouped by semantic fit to the research corpus.
                </p>
              </header>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', alignItems: 'start' }}>
                {columns.map((col) => (
                  <div key={col.title} className="glass-card" style={{ padding: '1.25rem', minWidth: 0 }}>
                    <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <col.icon size={18} color={col.color} />
                        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>{col.title}</h4>
                      </div>
                      <span className="badge" style={{ background: col.bg, color: col.color }}>{col.hint}</span>
                    </header>

                    {col.items.length ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                        {col.items.map((o) => {
                          const ft = fitTier(o.semantic_fit)
                          return (
                            <div key={o.id} style={{ padding: '0.9rem 1rem', borderRadius: 10, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                                <div style={{ minWidth: 0 }}>
                                  <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.85rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{o.title}</div>
                                  <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <Building2 size={11} /> {o.funder}
                                  </div>
                                </div>
                                {o.semantic_fit !== null && o.semantic_fit !== undefined && (
                                  <span style={{
                                    width: '40px', height: '40px', borderRadius: '50%', flexShrink: 0,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    fontSize: '0.78rem', fontWeight: 800,
                                    color: ft.color, border: `2px solid ${ft.color}`, background: 'rgba(255,255,255,0.03)'
                                  }}>
                                    {o.semantic_fit}%
                                  </span>
                                )}
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', marginTop: '0.55rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                  <IndianRupee size={11} /> {o.amount_range || '—'}
                                </span>
                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                  <CalendarDays size={11} /> {toDate(o.deadline)}
                                </span>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', border: '1px dashed var(--border-color)', borderRadius: 10 }}>
                        No opportunities here yet.
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* Sector landscape */}
            {hotSectors.length > 0 && (
              <section className="glass-card" style={{ padding: '1.5rem' }}>
                <header style={{ marginBottom: '1.1rem' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>Sector Momentum</h3>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Where research volume meets open funding — strongest domains first.
                  </p>
                </header>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.1rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                    {hotSectors.map((h, i) => (
                      <div key={i}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.3rem' }}>
                          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{h.domain}</span>
                          <span style={{ fontSize: '0.78rem', color: '#fbbf24', fontWeight: 700 }}>{h.avg_semantic_fit ?? 0}% fit</span>
                        </div>
                        <div style={{ height: '8px', borderRadius: 999, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                          <div style={{
                            height: '100%', borderRadius: 999,
                            width: `${Math.max(6, Math.round((h.publication_count / maxPubs) * 100))}%`,
                            background: 'linear-gradient(90deg, var(--accent-emerald) 0%, #f59e0b 100%)'
                          }} />
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                          {fmt(h.publication_count)} publications · {fmt(h.funding_count)} funding tracks
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}

            {/* Funders engagement */}
            <section className="glass-card" style={{ padding: '1.5rem' }}>
              <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>My Engagement</h3>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Applications and actions tied to your account.
                  </p>
                </div>
                <Link to="/funding" className="btn-secondary" style={{ padding: '0.45rem 1rem', fontSize: '0.8rem' }}>Browse Opportunities</Link>
              </header>

              {myApps.length ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                  {myApps.map((app) => (
                    <div key={app.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.9rem 1.1rem', borderRadius: 10, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)' }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{app.title}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{app.funder} · {app.amount_range} · {toDate(app.submitted_at)}</div>
                      </div>
                      <span className="badge" style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', textTransform: 'capitalize', whiteSpace: 'nowrap' }}>{app.status}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem', border: '1px dashed var(--border-color)', borderRadius: 12 }}>
                  No engagement yet. Explore the pipeline above and track opportunities that fit your thesis.
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </AppLayout>
  )
}

export default FunderDashboard