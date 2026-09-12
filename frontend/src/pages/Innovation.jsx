import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import patentAnalyticsService from '../services/patentAnalytics'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, AreaChart, Area, Cell
} from 'recharts'
import { Lightbulb, TrendingUp, FileText, Target, AlertCircle, ArrowUpRight, ArrowDownRight, Database, RefreshCw } from 'lucide-react'

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#64748b']
const compact = (n) => n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(0) + 'K' : String(n)

function Panel({ title, subtitle, children, style = {} }) {
  return (
    <div className="glass-card" style={{ padding: '1.5rem', ...style }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{title}</h3>
      {subtitle ? <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0 0 1rem 0' }}>{subtitle}</p> : null}
      {children}
    </div>
  )
}

function Innovation() {
  const [domains, setDomains] = useState([])
  const [trends, setTrends] = useState([])
  const [growth, setGrowth] = useState([])
  const [overlap, setOverlap] = useState([])
  const [opportunities, setOpportunities] = useState([])
  const [landscape, setLandscape] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingLandscape, setLoadingLandscape] = useState(true)
  const [error, setError] = useState('')
  const [landscapeError, setLandscapeError] = useState('')

  const loadPatents = async () => {
    setError('')
    try {
      const [dom, trn, grw, ovl, opp] = await Promise.all([
        patentAnalyticsService.domains(),
        patentAnalyticsService.trends(),
        patentAnalyticsService.growth(),
        patentAnalyticsService.researchOverlap(),
        patentAnalyticsService.opportunities()
      ])
      setDomains(dom)
      setTrends(trn)
      setGrowth(grw)
      setOverlap(ovl)
      setOpportunities(opp)
    } catch (err) {
      setError('Patent analytics are unavailable right now.')
    }
  }

  const loadLandscape = async () => {
    setLandscapeError('')
    try {
      const data = await patentAnalyticsService.researchLandscape()
      setLandscape(data)
    } catch (err) {
      setLandscapeError('Research landscape could not be loaded.')
    } finally {
      setLoadingLandscape(false)
    }
  }

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      await Promise.all([loadPatents(), loadLandscape()])
      setLoading(false)
    }
    run()
  }, [])

  const refresh = async () => {
    setLoading(true)
    setLoadingLandscape(true)
    await Promise.all([loadPatents(), loadLandscape()])
    setLoading(false)
  }

  const totalPatents = domains.reduce((s, d) => s + d.count, 0)
  const uniqueDomains = domains.length
  const growingFields = growth.filter(g => g.growth_rate > 20).length

  const topGrowth = [...growth]
    .filter(g => g.year === Math.max(...growth.map(x => x.year), 0))
    .sort((a, b) => b.growth_rate - a.growth_rate)
    .slice(0, 6)

  const maxPub = landscape?.hot_domains?.length ? Math.max(...landscape.hot_domains.map(h => h.publication_count)) : 1

  return (
    <AppLayout title="Patent & Innovation Intelligence" subtitle="Analyze patent activity, the global research landscape, and innovation opportunities">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1400px', margin: '0 auto' }}>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button onClick={refresh} className="btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {loading && <p style={{ color: 'var(--text-secondary)', padding: '3rem', textAlign: 'center' }}>Loading innovation intelligence…</p>}

        {/* ============ RESEARCH LANDSCAPE (global corpus) ============ */}
        {!loading && landscape && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <Database size={22} style={{ color: '#3b82f6', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{compact(landscape.total_publications || 0)}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Global Research Corpus</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <Target size={22} style={{ color: '#8b5cf6', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{landscape.open_funding_count || 0}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Open Funding Tracks</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <Lightbulb size={22} style={{ color: '#f59e0b', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{landscape.hot_domains?.length || 0}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Active Research Domains</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <TrendingUp size={22} style={{ color: '#10b981', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{landscape.publication_trends?.length || 0}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Years Tracked</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <Panel title="Research Publication Trends" subtitle="Global corpus indexed per year">
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={landscape.publication_trends || []} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="lcTrendFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} labelStyle={{ color: '#e2e8f0' }} />
                    <Area type="monotone" dataKey="count" name="Publications" stroke="#10b981" fill="url(#lcTrendFill)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </Panel>

              <Panel title="Leading Research Topics" subtitle="Most active topics across the corpus">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={(landscape.top_primary_topics || []).slice(0, 8)} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis dataKey="name" type="category" width={150} tick={{ fill: '#cbd5e1', fontSize: 11 }} />
                    <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} labelStyle={{ color: '#e2e8f0' }} />
                    <Bar dataKey="count" name="Publications" radius={[0, 6, 6, 0]}>
                      {(landscape.top_primary_topics || []).slice(0, 8).map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            {landscape.hot_domains?.length > 0 && (
              <Panel title="Hot Research ↔ Funding Domains" subtitle="Where global research meets open funding opportunities">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                  {landscape.hot_domains.map((h, i) => (
                    <div key={i} className="glass-card" style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{h.domain}</span>
                        <span className="badge badge-blue" style={{ fontSize: '0.75rem' }}>{h.avg_semantic_fit}% fit</span>
                      </div>
                      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        <div style={{ flexGrow: 1, height: '8px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.08)' }}>
                          <div style={{ width: `${Math.max(4, (h.publication_count / maxPub) * 100)}%`, height: '100%', borderRadius: '999px', background: 'linear-gradient(90deg, #06b6d4, #6366f1)' }} />
                        </div>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>{compact(h.publication_count)} pubs</span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>{h.funding_count} open funding track(s)</div>
                    </div>
                  ))}
                </div>
              </Panel>
            )}
          </>
        )}

        {!loading && landscapeError && (
          <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
            <AlertCircle size={28} style={{ color: '#f59e0b', marginBottom: '0.5rem' }} />
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{landscapeError}</p>
          </div>
        )}

        {/* ============ PATENT ANALYTICS ============ */}
        {!loading && error && totalPatents === 0 && (
          <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
            <AlertCircle size={32} style={{ color: '#f59e0b', marginBottom: '1rem' }} />
            <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>{error}</p>
          </div>
        )}

        {!loading && !error && totalPatents === 0 && (
          <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
            <FileText size={40} style={{ color: 'var(--primary-color)', marginBottom: '1rem', opacity: 0.5 }} />
            <h3 style={{ color: 'var(--text-primary)', fontSize: '1.15rem', marginBottom: '0.5rem' }}>Your patent portfolio</h3>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '440px', margin: '0 auto' }}>
              No patents added yet — add some on the Patents page and your personal filing analytics will appear below.
            </p>
          </div>
        )}

        {!loading && !error && totalPatents > 0 && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <FileText size={22} style={{ color: '#3b82f6', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{totalPatents}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Total Patents</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <Target size={22} style={{ color: '#8b5cf6', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{uniqueDomains}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Technology Domains</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <TrendingUp size={22} style={{ color: '#10b981', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{growingFields}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Growing Fields</div>
              </div>
              <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                <Lightbulb size={22} style={{ color: '#f59e0b', marginBottom: '0.5rem' }} />
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{opportunities.length}</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Innovation Opportunities</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
              <Panel title="Patents by Technology Domain">
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={domains.slice(0, 10)} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis dataKey="domain" type="category" width={150} tick={{ fill: '#cbd5e1', fontSize: 11 }} />
                    <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} labelStyle={{ color: '#e2e8f0' }} />
                    <Bar dataKey="count" name="Patents" radius={[0, 6, 6, 0]}>
                      {domains.slice(0, 10).map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Panel>

              <Panel title="Filing Trends Over Time">
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={trends} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="year" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid var(--border-color)', backgroundColor: '#0f172a' }} labelStyle={{ color: '#e2e8f0' }} />
                    <Area type="monotone" dataKey="count" name="Patents Filed" stroke="#3b82f6" fill="url(#trendFill)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            {topGrowth.length > 0 && (
              <Panel title="Fastest Growing Domains" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  {topGrowth.map((g, i) => (
                    <div key={i} className="glass-card" style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 600 }}>{g.domain}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{g.count} patents in {g.year}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        {g.growth_rate > 0
                          ? <ArrowUpRight size={16} style={{ color: '#10b981' }} />
                          : <ArrowDownRight size={16} style={{ color: '#ef4444' }} />
                        }
                        <span style={{ fontSize: '0.875rem', fontWeight: 700, color: g.growth_rate > 0 ? '#10b981' : '#ef4444' }}>
                          {g.growth_rate > 0 ? '+' : ''}{g.growth_rate}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Panel>
            )}

            {overlap.length > 0 && (
              <Panel title="Research ↔ Patent Overlap" style={{ marginBottom: '1.5rem' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-secondary)' }}>Domain</th>
                        <th style={{ textAlign: 'right', padding: '0.75rem', color: 'var(--text-secondary)' }}>Patents</th>
                        <th style={{ textAlign: 'right', padding: '0.75rem', color: 'var(--text-secondary)' }}>Publications</th>
                        <th style={{ textAlign: 'right', padding: '0.75rem', color: 'var(--text-secondary)' }}>Concepts</th>
                        <th style={{ textAlign: 'right', padding: '0.75rem', color: 'var(--text-secondary)' }}>Total Research</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overlap.map((row, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 500 }}>{row.domain}</td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', color: '#3b82f6', fontWeight: 600 }}>{row.patent_count}</td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', color: 'var(--text-primary)' }}>{row.publication_count}</td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', color: 'var(--text-primary)' }}>{row.concept_count}</td>
                          <td style={{ padding: '0.75rem', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 600 }}>{row.total_research}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            )}

            {opportunities.length > 0 && (
              <Panel title="Innovation Opportunities">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                  {opportunities.map((opp, i) => (
                    <div key={i} className="glass-card" style={{ padding: '1.25rem', borderLeft: '3px solid #f59e0b' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{opp.domain}</span>
                        <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: 999, backgroundColor: 'rgba(245,158,11,0.15)', color: '#fbbf24', fontWeight: 600 }}>
                          Gap: {opp.gap_score}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                        {opp.opportunity}
                      </p>
                    </div>
                  ))}
                </div>
              </Panel>
            )}
          </>
        )}
      </div>
    </AppLayout>
  )
}

export default Innovation