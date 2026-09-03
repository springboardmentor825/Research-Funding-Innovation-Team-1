import React, { useEffect, useState } from 'react'
import Navbar from '../components/common/Navbar'
import patentAnalyticsService from '../services/patentAnalytics'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, AreaChart, Area, Cell
} from 'recharts'
import { Lightbulb, TrendingUp, FileText, Target, AlertCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react'

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#64748b']
const compact = (n) => n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(0) + 'K' : String(n)

function Panel({ title, children, style = {} }) {
  return (
    <div className="glass-card" style={{ padding: '1.5rem', ...style }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem' }}>{title}</h3>
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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => { loadAll() }, [])

  const loadAll = async () => {
    setLoading(true)
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
      setError('Failed to load patent analytics. Add patents from the Patents page first.')
    } finally {
      setLoading(false)
    }
  }

  const totalPatents = domains.reduce((s, d) => s + d.count, 0)
  const uniqueDomains = domains.length
  const growingFields = growth.filter(g => g.growth_rate > 20).length

  const topGrowth = [...growth]
    .filter(g => g.year === Math.max(...growth.map(x => x.year), 0))
    .sort((a, b) => b.growth_rate - a.growth_rate)
    .slice(0, 6)

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-gradient)' }}>
      <Navbar />
      <div style={{ padding: '0 2rem 2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>Patent & Innovation Intelligence</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Analyze patent activity, technology trends, and innovation opportunities</p>
          </div>
          <button onClick={loadAll} className="btn-primary" style={{ padding: '0.5rem 1.25rem', fontSize: '0.875rem' }}>Refresh</button>
        </div>

        {loading && <p style={{ color: 'var(--text-secondary)', padding: '3rem', textAlign: 'center' }}>Loading patent analytics...</p>}
        {error && (
          <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
            <AlertCircle size={32} style={{ color: '#f59e0b', marginBottom: '1rem' }} />
            <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>{error}</p>
          </div>
        )}

        {!loading && !error && totalPatents === 0 && (
          <div className="glass-card" style={{ padding: '4rem', textAlign: 'center' }}>
            <FileText size={48} style={{ color: 'var(--primary-color)', marginBottom: '1rem', opacity: 0.5 }} />
            <h3 style={{ color: 'var(--text-primary)', fontSize: '1.25rem', marginBottom: '0.5rem' }}>No patents yet</h3>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
              Go to the Patents page and add some patents. The analytics will appear here automatically.
            </p>
          </div>
        )}

        {!loading && !error && totalPatents > 0 && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
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
    </div>
  )
}

export default Innovation
