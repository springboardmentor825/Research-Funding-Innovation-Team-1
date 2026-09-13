import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import adminService from '../../services/admin'
import { Users, DollarSign, Sparkles, BookOpen, Award, Shield, AlertTriangle, ArrowRight, CheckCircle2, Activity } from 'lucide-react'

function AdminDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminService.getDashboard()
      setData(res)
    } catch (err) {
      console.error('Admin Dashboard fetch error:', err)
      setError('Unable to load Administrator Dashboard. Please verify backend connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const summary = data?.summary || {}
  const roles = data?.users_by_role || {}
  const recentUsers = data?.recent_users || []
  const systemStatus = data?.system_status || {}

  return (
    <AppLayout
      title="Administrator Control Center"
      subtitle="Executive platform health monitoring, user management, and system intelligence"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>

        {/* Executive Header Banner */}
        <div 
          className="ai-card"
          style={{
            padding: '1.75rem 2rem',
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1.25rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '14px',
              background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)'
            }}>
              <Shield size={30} color="#FFFFFF" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#F8FAFC', margin: 0 }}>
                Platform System Overview
              </h2>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: '0.25rem 0 0 0' }}>
                Canonical Administrator Workspace • System-wide control & monitoring
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <Link to="/admin/users" className="btn-ai-primary" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.15rem' }}>
              <Users size={16} />
              <span>Manage Users</span>
            </Link>
            <Link to="/admin/reports" className="btn-ai-outline" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.15rem' }}>
              <BookOpen size={16} />
              <span>System Reports</span>
            </Link>
          </div>
        </div>

        {/* Loading / Error States */}
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading Administrator Metrics...
          </div>
        ) : error ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: '#EF4444', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
            <AlertTriangle size={36} style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.5rem' }}>Unable to Load Data</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>{error}</p>
            <button onClick={fetchDashboardData} className="btn-ai-primary" style={{ padding: '0.55rem 1.35rem' }}>
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* Top KPI Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
              
              {/* Total Users */}
              <div className="ai-card" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Total Users
                  </span>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Users size={18} color="var(--accent-cyan-light)" />
                  </div>
                </div>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', lineHeight: 1 }}>
                  {summary.total_users ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                  {summary.active_users ?? 0} Active Accounts
                </div>
              </div>

              {/* Funding Opportunities */}
              <div className="ai-card" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Funding Opps
                  </span>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <DollarSign size={18} color="var(--accent-emerald)" />
                  </div>
                </div>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', lineHeight: 1 }}>
                  {summary.funding_opportunities ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)' }}>
                  {summary.active_funding_opportunities ?? 0} Open Grants
                </div>
              </div>

              {/* Recommendations Generated */}
              <div className="ai-card" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    AI Recommendations
                  </span>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(168, 85, 247, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Sparkles size={18} color="#C084FC" />
                  </div>
                </div>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', lineHeight: 1 }}>
                  {summary.recommendations_generated ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: '#C084FC', fontWeight: 600 }}>
                  Active Scoring Engine
                </div>
              </div>

              {/* Research Profiles */}
              <div className="ai-card" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Research Profiles
                  </span>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(59, 130, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <BookOpen size={18} color="#60A5FA" />
                  </div>
                </div>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', lineHeight: 1 }}>
                  {summary.research_profiles ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)' }}>
                  {summary.publications ?? 0} Publications
                </div>
              </div>

              {/* Patents */}
              <div className="ai-card" style={{ padding: '1.35rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Patent Assets
                  </span>
                  <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Award size={18} color="#FBBF24" />
                  </div>
                </div>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC', lineHeight: 1 }}>
                  {summary.patents ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: '#FBBF24', fontWeight: 600 }}>
                  IP Asset Records
                </div>
              </div>

            </div>

            {/* Middle Section: User Role Distribution & System Services */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
              
              {/* User Roles Breakdown */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Users size={18} color="var(--accent-cyan)" /> Users by Canonical Role
                  </h3>
                  <Link to="/admin/users" style={{ fontSize: '0.8rem', color: 'var(--accent-cyan-light)', textDecoration: 'none', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <span>Manage</span> <ArrowRight size={13} />
                  </Link>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {[
                    { key: 'researcher', label: 'Researchers', count: roles.researcher || 0, color: 'var(--accent-cyan)' },
                    { key: 'startup_founder', label: 'Startup Founders', count: roles.startup_founder || 0, color: 'var(--accent-emerald)' },
                    { key: 'administrator', label: 'Administrators', count: roles.administrator || 0, color: '#C084FC' }
                  ].map((rItem) => {
                    const total = summary.total_users || 1
                    const pct = Math.round((rItem.count / total) * 100)
                    return (
                      <div key={rItem.key} style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>{rItem.label}</span>
                          <span style={{ color: 'var(--text-secondary)' }}>{rItem.count} ({pct}%)</span>
                        </div>
                        <div style={{ height: '8px', width: '100%', borderRadius: '4px', background: 'rgba(30, 41, 59, 0.8)', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${pct}%`, background: rItem.color, transition: 'width 0.4s ease' }} />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* System Service Health Status */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity size={18} color="var(--accent-emerald)" /> Platform System Health
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {[
                    { label: 'MySQL Relational Database', status: systemStatus.database || 'online' },
                    { label: 'AI Recommendation Scoring Engine', status: systemStatus.ai_matching_engine || 'online' },
                    { label: 'FAISS Vector Search & RAG Assistant', status: systemStatus.rag_service || 'online' },
                    { label: 'Role Authorization & JWT Service', status: systemStatus.auth_service || 'online' }
                  ].map((srv, sIdx) => (
                    <div 
                      key={sIdx}
                      style={{
                        padding: '0.75rem 1rem',
                        borderRadius: '10px',
                        background: 'rgba(30, 41, 59, 0.5)',
                        border: '1px solid var(--border-color)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}
                    >
                      <span style={{ fontSize: '0.875rem', color: '#E2E8F0', fontWeight: 500 }}>{srv.label}</span>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        padding: '0.2rem 0.6rem',
                        borderRadius: '9999px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        color: 'var(--accent-emerald)',
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        textTransform: 'uppercase'
                      }}>
                        <CheckCircle2 size={12} /> {srv.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Bottom Section: Recent User Registrations */}
            <div className="ai-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Users size={18} color="var(--accent-cyan)" /> Recent User Registrations
                </h3>
                <Link to="/admin/users" style={{ fontSize: '0.85rem', color: 'var(--accent-cyan-light)', textDecoration: 'none', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span>View All Users</span> <ArrowRight size={14} />
                </Link>
              </div>

              {recentUsers.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                  No recent user signups recorded in database.
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>User ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Full Name</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Email</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Canonical Role</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Auth Provider</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Registered At</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentUsers.map((u) => (
                        <tr key={u.id} style={{ borderBottom: '1px solid rgba(30, 41, 59, 0.6)' }}>
                          <td style={{ padding: '0.75rem 1rem', color: 'var(--accent-cyan-light)', fontWeight: 700 }}>#{u.id}</td>
                          <td style={{ padding: '0.75rem 1rem', color: '#F8FAFC', fontWeight: 600 }}>{u.full_name}</td>
                          <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{u.email}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <span style={{
                              fontSize: '0.75rem',
                              padding: '0.2rem 0.65rem',
                              borderRadius: '12px',
                              fontWeight: 700,
                              background: u.role === 'administrator' ? 'rgba(168, 85, 247, 0.2)' : u.role === 'startup_founder' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                              color: u.role === 'administrator' ? '#C084FC' : u.role === 'startup_founder' ? '#10B981' : 'var(--accent-cyan-light)'
                            }}>
                              {u.role}
                            </span>
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{u.auth_provider}</td>
                          <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>{u.created_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

          </>
        )}

      </div>
    </AppLayout>
  )
}

export default AdminDashboard
