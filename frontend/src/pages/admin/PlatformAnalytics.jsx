import React, { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import adminService from '../../services/admin'
import { Sparkles, Users, DollarSign, BookOpen, Award, AlertTriangle, BarChart3, PieChart, TrendingUp, Activity } from 'lucide-react'

function PlatformAnalytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await adminService.getAnalytics()
      setAnalytics(data)
    } catch (err) {
      console.error('Analytics fetch error:', err)
      setError('Unable to load platform analytics data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const usersA = analytics?.user_analytics || {}
  const fundingA = analytics?.funding_analytics || {}
  const researchA = analytics?.research_analytics || {}
  const patentA = analytics?.patent_analytics || {}

  return (
    <AppLayout
      title="Platform Intelligence Analytics"
      subtitle="Comprehensive data breakdown across Users, Grants, Academic Output, and Patent Portfolios"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>

        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Aggregating platform intelligence metrics...
          </div>
        ) : error ? (
          <div className="ai-card" style={{ padding: '3rem', textAlign: 'center', color: '#EF4444' }}>
            <AlertTriangle size={36} style={{ marginBottom: '0.75rem' }} />
            <h3>Unable to Load Analytics</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>{error}</p>
            <button onClick={fetchAnalytics} className="btn-ai-primary" style={{ padding: '0.5rem 1.25rem' }}>
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* Grid 1: User & Funding Analytics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
              
              {/* User Roles & Auth Providers */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Users size={18} color="var(--accent-cyan)" /> User Distribution & Auth Channels
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Users by Role</div>
                  {Object.entries(usersA.roles_breakdown || {}).map(([rKey, rCount]) => {
                    const total = usersA.total_users || 1
                    const pct = Math.round((rCount / total) * 100)
                    return (
                      <div key={rKey} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem' }}>
                          <span style={{ color: '#E2E8F0', textTransform: 'capitalize' }}>{rKey.replace('_', ' ')}</span>
                          <span style={{ color: 'var(--text-secondary)' }}>{rCount} ({pct}%)</span>
                        </div>
                        <div style={{ height: '8px', width: '100%', borderRadius: '4px', background: 'rgba(30, 41, 59, 0.8)', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${pct}%`, background: 'var(--accent-cyan)' }} />
                        </div>
                      </div>
                    )
                  })}

                  <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.85rem', marginTop: '0.5rem' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '0.5rem' }}>Authentication Providers</div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      {Object.entries(usersA.auth_providers || {}).map(([pName, pCount]) => (
                        <div key={pName} style={{ flex: 1, padding: '0.75rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '8px', border: '1px solid var(--border-color)', textTransform: 'capitalize' }}>
                          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F8FAFC' }}>{pCount}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{pName} Auth</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Funding Agency Breakdown */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <DollarSign size={18} color="var(--accent-emerald)" /> Funding Agencies & Grant Concentration
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {(fundingA.top_funders || []).length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No funding agency records available.</div>
                  ) : (
                    fundingA.top_funders.map((fItem, fIdx) => (
                      <div key={fIdx} style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '0.875rem', color: '#E2E8F0', fontWeight: 600 }}>{fItem.funder}</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-emerald)', padding: '0.15rem 0.6rem', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.15)' }}>
                          {fItem.count} Grants
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </div>

            {/* Grid 2: Research & Patent Analytics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
              
              {/* Top Research Domains */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <BookOpen size={18} color="#60A5FA" /> Primary Research Domains
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {(researchA.top_domains || []).length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No research domain profiles recorded.</div>
                  ) : (
                    researchA.top_domains.map((dItem, dIdx) => (
                      <div key={dIdx} style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '0.875rem', color: '#E2E8F0', fontWeight: 600 }}>{dItem.domain || 'Unspecified'}</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#60A5FA', padding: '0.15rem 0.6rem', borderRadius: '12px', background: 'rgba(96, 165, 250, 0.15)' }}>
                          {dItem.count} Profiles
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Patent Technology Domains */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Award size={18} color="#FBBF24" /> Patent Technology Domains
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {(patentA.top_domains || []).length === 0 ? (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No patent technology assets registered.</div>
                  ) : (
                    patentA.top_domains.map((pItem, pIdx) => (
                      <div key={pIdx} style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '0.875rem', color: '#E2E8F0', fontWeight: 600 }}>{pItem.domain || 'General IP'}</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#FBBF24', padding: '0.15rem 0.6rem', borderRadius: '12px', background: 'rgba(245, 158, 11, 0.15)' }}>
                          {pItem.count} Assets
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </div>
          </>
        )}

      </div>
    </AppLayout>
  )
}

export default PlatformAnalytics
