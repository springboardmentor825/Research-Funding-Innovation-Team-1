import React, { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
  ResponsiveContainer,
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, Cell,
  PieChart, Pie, Legend
} from 'recharts'
import Navbar from '../components/common/Navbar'
import { useAuth } from '../context/AuthContext'
import publicationsService from '../services/publications'
import patentsService from '../services/patents'
import analyticsService from '../services/analytics'

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#64748b']

const fmt = (n) => (n === null || n === undefined ? '—' : Number(n).toLocaleString())

function KpiCard({ label, value, sub, color = 'var(--primary-color)' }) {
  return (
    <div className="glass-card" style={{ padding: '1.5rem' }}>
      <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</p>
      <p style={{ margin: '0.5rem 0 0 0', fontSize: '2rem', fontWeight: 800, color, lineHeight: 1.1 }}>{value}</p>
      {sub ? <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{sub}</p> : null}
    </div>
  )
}

function Panel({ title, subtitle, children, style }) {
  return (
    <div className="glass-card" style={{ padding: '1.5rem', ...style }}>
      <h3 style={{ fontSize: '1.1rem', margin: '0 0 0.25rem 0', fontWeight: 700, color: 'var(--text-primary)' }}>{title}</h3>
      {subtitle ? <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{subtitle}</p> : null}
      {children}
    </div>
  )
}

function ChartShell({ height = 300, children }) {
  return (
    <div style={{ width: '100%', height, fontSize: '0.85rem' }}>
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  )
}

function Dashboard() {
  const { user } = useAuth()
  const [pubCount, setPubCount] = useState(0)
  const [patentCount, setPatentCount] = useState(0)
  const [loadingPortfolio, setLoadingPortfolio] = useState(true)

  const [overview, setOverview] = useState(null)
  const [trends, setTrends] = useState([])
  const [types, setTypes] = useState([])
  const [topics, setTopics] = useState([])
  const [topCited, setTopCited] = useState([])
  const [oaStatus, setOaStatus] = useState([])
  const [retraction, setRetraction] = useState([])
  const [analyticsLoading, setAnalyticsLoading] = useState(true)
  const [analyticsError, setAnalyticsError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const pubs = await publicationsService.list()
        const patents = await patentsService.list()
        setPubCount(pubs.length)
        setPatentCount(patents.length)
      } catch (err) {
        console.error('Failed to load portfolio stats:', err)
      } finally {
        setLoadingPortfolio(false)
      }
    }
    fetchStats()
  }, [])

  const fetchAnalytics = useCallback(async () => {
    setAnalyticsLoading(true)
    setAnalyticsError(null)
    try {
      const [ov, tr, ty, to, tc, oa, rt] = await Promise.all([
        analyticsService.overview(),
        analyticsService.publicationTrends(),
        analyticsService.publicationTypes(),
        analyticsService.topics(10),
        analyticsService.topCited(10),
        analyticsService.openAccessStatus(),
        analyticsService.retractionStatus()
      ])
      setOverview(ov)
      setTrends(tr)
      setTypes(ty)
      setTopics(to)
      setTopCited(tc)
      setOaStatus(oa)
      setRetraction(rt)
    } catch (err) {
      console.error('Failed to load analytics:', err)
      setAnalyticsError('Could not load research analytics. Is the backend running?')
    } finally {
      setAnalyticsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--dark-bg)' }}>
      <Navbar />
      <div style={{ padding: '0 2rem 2rem 2rem', display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', width: '100%', margin: '0 auto' }}>

        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary-color)', margin: 0 }}>
              Intelligence Dashboard
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Welcome, {user?.full_name || 'Researcher'}. Access your portfolio, funding details, and intelligence modules.</p>
          </div>
          <span className="badge badge-blue">{user?.role || 'User'}</span>
        </header>

        {/* Overview Stats Cards */}
        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>

          <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>Research Profile</h3>
            {user?.profile ? (
              <div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                  <strong>{user.profile.designation}</strong> at {user.profile.organization}
                </p>
                <Link to="/profile" className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>View Profile</Link>
              </div>
            ) : (
              <div>
                <p style={{ color: '#ef4444', fontSize: '0.9rem', marginBottom: '1rem', fontWeight: 500 }}>No active profile details found.</p>
                <Link to="/profile" className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>Initialize Profile</Link>
              </div>
            )}
          </div>

          <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>My Publications</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Manage journals, authored studies, and index DOIs.</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--primary-color)' }}>{loadingPortfolio ? '...' : pubCount}</span>
              <Link to="/publications" className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>Manage</Link>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>My Patents</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Track filed intellectual properties, technology scopes, and inventors.</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--secondary-color)' }}>{loadingPortfolio ? '...' : patentCount}</span>
              <Link to="/patents" className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>Manage</Link>
            </div>
          </div>

        </section>

        {/* Features Modules */}
        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>

          <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem', color: 'var(--primary-color)' }}>Funding Opportunities</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Scan institutional funding tracks, eligibility demands, and submit research applications.</p>
            <Link to="/funding" className="btn-primary">Explore Schemes</Link>
          </div>

          <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)' }}>
            <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem', color: 'var(--secondary-color)' }}>Innovation Hub Projects</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Collaborate on active innovation tasks, technology pipelines, and intellectual assets.</p>
            <Link to="/innovation" className="btn-primary">View Projects</Link>
          </div>

        </section>

        {/* Research Intelligence Dashboard (global OpenAlex corpus) */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary-color)', margin: 0 }}>Research Intelligence</h2>
              <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0 0' }}>Live analytics across the global OpenAlex corpus of {overview ? fmt(overview.total_publications) : '50,000'} scholarly publications.</p>
            </div>
            <button
              className="btn-secondary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              onClick={fetchAnalytics}
              disabled={analyticsLoading}
            >
              {analyticsLoading ? 'Refreshing…' : 'Refresh'}
            </button>
          </header>

          {analyticsError ? (
            <div className="glass-card" style={{ padding: '2rem', backgroundColor: 'rgba(255,255,255,0.03)', textAlign: 'center' }}>
              <p style={{ color: '#ef4444', fontWeight: 600 }}>{analyticsError}</p>
              <button className="btn-primary" style={{ marginTop: '0.5rem' }} onClick={fetchAnalytics}>Retry</button>
            </div>
          ) : (
            <>
              {/* KPI Cards */}
              <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
                <KpiCard label="Total Publications" value={overview ? fmt(overview.total_publications) : '…'} color="var(--primary-color)" />
                <KpiCard label="Total Citations" value={overview ? fmt(overview.total_citations) : '…'} color="var(--secondary-color)" />
                <KpiCard label="Avg Citations" value={overview ? fmt(overview.avg_citations) : '…'} sub="per publication" color="#f59e0b" />
                <KpiCard
                  label="Open Access"
                  value={overview ? `${fmt(overview.open_access_count)}` : '…'}
                  sub={overview ? `${overview.open_access_pct}% of corpus` : ''}
                  color="#10b981"
                />
                <KpiCard label="Distinct Authors" value={overview ? fmt(overview.distinct_authors) : '…'} color="#06b6d4" />
                <KpiCard label="Distinct Institutions" value={overview ? fmt(overview.distinct_institutions) : '…'} color="#ec4899" />
              </section>

              {/* Charts */}
              <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.5rem' }}>

                <Panel title="Publication Trends" subtitle="Publications indexed per year" style={{ gridColumn: '1 / -1' }}>
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <ChartShell height={300}>
                      <AreaChart data={trends} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <defs>
                          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={fmt} width={70} />
                        <Tooltip formatter={(value) => [fmt(value), 'Publications']} labelStyle={{ color: '#e2e8f0' }} contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} />
                        <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fill="url(#trendFill)" name="Publications" />
                      </AreaChart>
                    </ChartShell>
                  )}
                </Panel>

                <Panel title="Publication Types" subtitle="Distribution across document types">
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <ChartShell height={280}>
                      <PieChart>
                        <Pie data={types} dataKey="count" nameKey="type" cx="50%" cy="50%" innerRadius={55} outerRadius={95} paddingAngle={2}>
                          {types.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                        </Pie>
                        <Tooltip formatter={(value, name) => [fmt(value), name]} contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} />
                        <Legend verticalAlign="bottom" height={36} formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: 12 }}>{value}</span>} />
                      </PieChart>
                    </ChartShell>
                  )}
                </Panel>

                <Panel title="Top Topics" subtitle="Most frequent research topics">
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <ChartShell height={280}>
                      <BarChart data={topics} layout="vertical" margin={{ top: 5, right: 30, bottom: 5, left: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={fmt} />
                        <YAxis type="category" dataKey="name" width={220} tick={{ fill: '#cbd5e1', fontSize: 11 }} tickFormatter={(v) => (v.length > 26 ? `${v.slice(0, 26)}…` : v)} />
                        <Tooltip formatter={(value) => [fmt(value), 'Publications']} contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} />
                        <Bar dataKey="count" fill="#8b5cf6" radius={[0, 6, 6, 0]} />
                      </BarChart>
                    </ChartShell>
                  )}
                </Panel>

                <Panel title="Open Access vs Closed" subtitle="Share of the corpus that is freely available">
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <ChartShell height={280}>
                      <PieChart>
                        <Pie data={oaStatus} dataKey="count" nameKey="status" cx="50%" cy="50%" innerRadius={55} outerRadius={95}>
                          {oaStatus.map((entry, i) => <Cell key={i} fill={entry.status === 'Open Access' ? '#10b981' : '#94a3b8'} />)}
                        </Pie>
                        <Tooltip formatter={(value, name) => [fmt(value), name]} contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} />
                        <Legend verticalAlign="bottom" height={36} formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: 12 }}>{value}</span>} />
                      </PieChart>
                    </ChartShell>
                  )}
                </Panel>

                <Panel title="Retraction Status" subtitle="Retracted vs non-retracted publications">
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <ChartShell height={280}>
                      <BarChart data={retraction} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="status" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={fmt} width={70} />
                        <Tooltip formatter={(value) => [fmt(value), 'Publications']} contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} />
                        <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                          {retraction.map((entry, i) => <Cell key={i} fill={entry.status === 'Retracted' ? '#ef4444' : '#3b82f6'} />)}
                        </Bar>
                      </BarChart>
                    </ChartShell>
                  )}
                </Panel>

                <Panel title="Top Cited Papers" subtitle="Highest-impact publications in the corpus" style={{ gridColumn: '1 / -1' }}>
                  {analyticsLoading ? <p style={{ color: 'var(--text-secondary)' }}>Loading…</p> : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {topCited.map((paper, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.75rem 1rem', backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 10, border: '1px solid var(--border-color)' }}>
                          <span style={{ fontWeight: 800, color: 'var(--primary-color)', fontSize: '1.1rem', minWidth: '2rem' }}>#{i + 1}</span>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <p style={{ margin: 0, fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{paper.title}</p>
                            <p style={{ margin: '0.15rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                              {paper.year ? `${paper.year} · ` : ''}{paper.source || 'Unknown source'}{paper.authors ? ` · ${paper.authors}` : ''}
                            </p>
                          </div>
                          <span className="badge badge-blue" style={{ whiteSpace: 'nowrap' }}>{fmt(paper.cited_by_count)} citations</span>
                        </div>
                      ))}
                    </div>
                  )}
                </Panel>

              </section>
            </>
          )}
        </section>

      </div>
    </div>
  )
}

export default Dashboard