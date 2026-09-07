// frontend/src/pages/Dashboard.jsx

import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import { useAuth } from '../context/AuthContext'
import {
  getIntegratedDashboard,
  markAlertRead,
  dismissAlert,
  triggerAlertGeneration
} from '../services/researchIntelligence'
import fundingService from '../services/funding'
import {
  Sparkles,
  RefreshCw,
  AlertCircle,
  Search,
  Bell,
  CheckCircle,
  XCircle,
  User,
  Award,
  BookOpen,
  Lightbulb,
  Users,
  Clock,
  TrendingUp,
  ShieldCheck,
  Zap,
  Bookmark,
  ExternalLink,
  ChevronRight,
  BarChart2
} from 'lucide-react'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'

function Dashboard() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedRec, setSelectedRec] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [alertFilter, setAlertFilter] = useState('all') // all, high, medium, low

  const userId = user?.id || 16

  const loadDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getIntegratedDashboard(userId)
      setDashboardData(data)
    } catch (err) {
      console.error('Failed to load integrated dashboard:', err)
      setError('Unable to fetch live Integrated Research Intelligence data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      loadDashboard()
    }
  }, [userId])

  const handleMarkAlertRead = async (alertId) => {
    try {
      await markAlertRead(alertId, userId)
      setDashboardData((prev) => {
        if (!prev) return prev
        const updatedAlerts = (prev.alerts || []).map((a) =>
          a.id === alertId ? { ...a, is_read: true } : a
        )
        const unreadCount = updatedAlerts.filter((a) => !a.is_read).length
        return {
          ...prev,
          alerts: updatedAlerts,
          kpis: { ...prev.kpis, unread_alerts: unreadCount }
        }
      })
    } catch (err) {
      console.error('Failed to mark alert as read:', err)
    }
  }

  const handleDismissAlert = async (alertId) => {
    try {
      await dismissAlert(alertId, userId)
      setDashboardData((prev) => {
        if (!prev) return prev
        const updatedAlerts = (prev.alerts || []).filter((a) => a.id !== alertId)
        const unreadCount = updatedAlerts.filter((a) => !a.is_read).length
        return {
          ...prev,
          alerts: updatedAlerts,
          kpis: { ...prev.kpis, unread_alerts: unreadCount }
        }
      })
    } catch (err) {
      console.error('Failed to dismiss alert:', err)
    }
  }

  const handleFundingFeedback = async (fundingId, feedbackType) => {
    try {
      await fundingService.sendFeedback(userId, fundingId, feedbackType)
      loadDashboard()
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  const kpis = dashboardData?.kpis || {}
  const researcher = dashboardData?.researcher || {}
  const funding = dashboardData?.funding || {}
  const collaboration = dashboardData?.collaboration || {}
  const patents = dashboardData?.patents || {}
  const innovation = dashboardData?.innovation || {}
  const analytics = dashboardData?.analytics || {}
  const recentActivity = dashboardData?.recent_activity || []
  const alertsList = dashboardData?.alerts || []

  // Filter alerts
  const filteredAlerts = alertsList.filter((a) => {
    if (alertFilter === 'all') return true
    return a.priority === alertFilter
  })

  // Filter funding recommendations by global header search
  const safeRecs = funding.top_recommendations || []
  const filteredRecs = safeRecs.filter((r) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      (r.title && r.title.toLowerCase().includes(q)) ||
      (r.funder && r.funder.toLowerCase().includes(q)) ||
      (r.description && r.description.toLowerCase().includes(q))
    )
  })

  return (
    <AppLayout
      title="Integrated Research Intelligence Dashboard"
      subtitle="Unified AI Analytics, Grants, Peer Collaboration, Patents & Real-Time Alerts"
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Loading Spinner */}
        {loading && (
          <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--accent-cyan-light)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <RefreshCw size={36} className="glow-animation" style={{ animation: 'spin 2s linear infinite' }} />
            <div style={{ fontSize: '1.15rem', fontWeight: 600 }}>Aggregating Integrated Research Intelligence (Parts 1–11)...</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Gathering live data across Grants, Collaborators, Patents, Analytics, and Alerts</div>
          </div>
        )}

        {/* Error Alert */}
        {error && !loading && (
          <div className="ai-card" style={{ padding: '1.25rem', border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#F8FAFC' }}>
              <AlertCircle size={20} color="#EF4444" />
              <span>{error}</span>
            </div>
            <button onClick={loadDashboard} className="btn-ai-outline" style={{ fontSize: '0.8rem' }}>
              Retry API
            </button>
          </div>
        )}

        {!loading && dashboardData && (
          <>
            {/* 1. TOP RESEARCHER 360° HEADER BANNER */}
            <div className="ai-card" style={{ padding: '1.75rem', background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.7) 100%)', border: '1px solid var(--border-color)', borderRadius: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: 700, color: '#FFF' }}>
                      {researcher.researcher_name ? researcher.researcher_name.charAt(0) : 'R'}
                    </div>
                    <div>
                      <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F8FAFC', margin: 0, letterSpacing: '-0.02em' }}>
                        {researcher.researcher_name || user?.full_name || 'Researcher Intelligence Profile'}
                      </h1>
                      <div style={{ fontSize: '0.875rem', color: 'var(--accent-cyan-light)', fontWeight: 500 }}>
                        {researcher.designation || 'Principal Researcher'} • {researcher.organization || 'Stanford University'}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
                    {(researcher.research_domains || ['AI', 'Computer Science']).map((domain, i) => (
                      <span key={i} style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.25rem 0.65rem', borderRadius: '20px', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan-light)', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
                        {domain}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: '#94A3B8' }}>
                    <ShieldCheck size={16} color="var(--accent-emerald)" />
                    Profile Completeness: <strong style={{ color: '#F8FAFC' }}>{researcher.profile_completeness?.completeness_score || 95}%</strong>
                  </div>
                  <div style={{ width: '180px', height: '6px', background: 'rgba(51, 65, 85, 0.8)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${researcher.profile_completeness?.completeness_score || 95}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-emerald) 100%)' }} />
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                    Activity Score: {researcher.research_activity?.activity_score || 88.5}/100
                  </div>
                </div>
              </div>
            </div>

            {/* 2. TOP LEVEL AUTHORITATIVE KPI CARDS */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              <div className="ai-card" style={{ padding: '1.25rem', borderLeft: '4px solid var(--accent-cyan)' }}>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Active Grants</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0' }}>{kpis.active_funding || 0}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)' }}>{kpis.strong_matches || 0} High Fit Matches</div>
              </div>

              <div className="ai-card" style={{ padding: '1.25rem', borderLeft: '4px solid #F59E0B' }}>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Upcoming Deadlines</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0' }}>{kpis.upcoming_deadlines || 0}</div>
                <div style={{ fontSize: '0.75rem', color: '#FCD34D' }}>Due within 30 days</div>
              </div>

              <div className="ai-card" style={{ padding: '1.25rem', borderLeft: '4px solid #10B981' }}>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Potential Collaborators</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0' }}>{kpis.potential_collaborators || 0}</div>
                <div style={{ fontSize: '0.75rem', color: '#6EE7B7' }}>Evaluated in Network ({kpis.network_size || 0})</div>
              </div>

              <div className="ai-card" style={{ padding: '1.25rem', borderLeft: '4px solid #8B5CF6' }}>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Publications & Patents</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0' }}>{(kpis.publications || 0) + (kpis.patents || 0)}</div>
                <div style={{ fontSize: '0.75rem', color: '#C4B5FD' }}>{kpis.publications || 0} Pubs • {kpis.patents || 0} Patents</div>
              </div>

              <div className="ai-card" style={{ padding: '1.25rem', borderLeft: '4px solid #EC4899' }}>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase' }}>Active Alerts</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0' }}>{kpis.unread_alerts || 0}</div>
                <div style={{ fontSize: '0.75rem', color: '#F472B6' }}>Real-time Notifications</div>
              </div>
            </div>

            {/* 3. MAIN DASHBOARD GRID */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem' }}>
              
              {/* LEFT COLUMN CONTENT */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
                
                {/* SECTION 1: TOP FUNDING RECOMMENDATIONS */}
                <div className="ai-card" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Sparkles size={20} color="var(--accent-cyan)" />
                      Top Funding Recommendations
                    </h2>
                    <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Parts 4 & 5 Engines</span>
                  </div>

                  {filteredRecs.length === 0 ? (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#64748B' }}>No funding opportunities found.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {filteredRecs.slice(0, 4).map((rec, i) => (
                        <div key={rec.funding_id || i} style={{ padding: '1.25rem', borderRadius: '12px', background: 'rgba(30, 41, 59, 0.4)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                              <span style={{ fontSize: '0.8rem', fontWeight: 800, padding: '0.2rem 0.5rem', borderRadius: '6px', background: rec.match_score >= 80 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.2)', color: rec.match_score >= 80 ? '#10B981' : 'var(--accent-cyan-light)' }}>
                                {rec.match_score}% Match
                              </span>
                              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>{rec.title}</h3>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.35rem' }}>
                              Funder: <strong>{rec.funder}</strong> • Amount: <strong>${(rec.amount || 500000).toLocaleString()}</strong> • Deadline: <strong>{rec.deadline || 'Open'}</strong>
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button onClick={() => setSelectedRec(rec)} className="btn-ai-outline" style={{ fontSize: '0.75rem', padding: '0.4rem 0.75rem' }}>
                              Details
                            </button>
                            <button onClick={() => handleFundingFeedback(rec.funding_id, 'saved')} className="btn-ai-primary" style={{ fontSize: '0.75rem', padding: '0.4rem 0.75rem' }}>
                              Save
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* SECTION 2: COLLABORATION INTELLATION & PEER MATCHES */}
                <div className="ai-card" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Users size={20} color="#10B981" />
                      Top Collaboration Candidates
                    </h2>
                    <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Parts 7 & 10 Engines</span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                    {(collaboration.top_collaborators || []).slice(0, 2).map((col, i) => (
                      <div key={i} style={{ padding: '1.15rem', borderRadius: '12px', background: 'rgba(30, 41, 59, 0.4)', border: '1px solid var(--border-color)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>{col.name}</h3>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.2)', color: '#10B981' }}>
                            {col.score}% Match
                          </span>
                        </div>
                        <div style={{ fontSize: '0.775rem', color: '#94A3B8', marginTop: '0.25rem' }}>{col.organization} • {col.designation}</div>
                        <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--accent-cyan-light)' }}>
                          Shared Tech: {(col.shared_technologies || []).slice(0, 2).join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* SECTION 3: PATENT & INNOVATION TRENDS */}
                <div className="ai-card" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Award size={20} color="#8B5CF6" />
                      Patent & Emerging Technology Intelligence
                    </h2>
                    <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Parts 8 & 11 Engines</span>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.85rem' }}>
                    {(innovation.emerging_technologies || []).slice(0, 3).map((em, i) => (
                      <div key={i} style={{ flex: '1 1 200px', padding: '1rem', borderRadius: '10px', background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
                        <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#C4B5FD' }}>{em.technology}</div>
                        <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '0.25rem' }}>
                          Filing Acceleration: <strong>+{em.growth_rate}%</strong>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: '#64748B', marginTop: '0.15rem' }}>Active Patents: {em.patent_count}</div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* RIGHT COLUMN CONTENT (ALERTS & TIMELINE) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
                
                {/* ALERTS & NOTIFICATIONS PANEL */}
                <div className="ai-card" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Bell size={18} color="#EC4899" />
                      Alerts ({filteredAlerts.length})
                    </h2>
                    <select
                      value={alertFilter}
                      onChange={(e) => setAlertFilter(e.target.value)}
                      style={{ background: 'rgba(30, 41, 59, 0.8)', color: '#F8FAFC', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                    >
                      <option value="all">All Priorities</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>

                  {filteredAlerts.length === 0 ? (
                    <div style={{ padding: '1.5rem', textAlign: 'center', color: '#64748B', fontSize: '0.85rem' }}>No active alerts.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', maxHeight: '380px', overflowY: 'auto' }}>
                      {filteredAlerts.map((a) => (
                        <div key={a.id} style={{ padding: '0.85rem', borderRadius: '10px', background: a.priority === 'high' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(30, 41, 59, 0.6)', borderLeft: a.priority === 'high' ? '3px solid #EF4444' : '3px solid var(--accent-cyan)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#F8FAFC' }}>{a.title}</div>
                            <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '0.1rem 0.35rem', borderRadius: '4px', background: a.priority === 'high' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(6, 182, 212, 0.3)', color: '#FFF' }}>
                              {a.priority.toUpperCase()}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '0.35rem' }}>{a.message}</div>
                          
                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                            {!a.is_read && (
                              <button onClick={() => handleMarkAlertRead(a.id)} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan-light)', cursor: 'pointer', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                                <CheckCircle size={12} /> Mark Read
                              </button>
                            )}
                            <button onClick={() => handleDismissAlert(a.id)} style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                              <XCircle size={12} /> Dismiss
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* RECENT INTELLIGENCE TIMELINE */}
                <div className="ai-card" style={{ padding: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Clock size={18} color="var(--accent-cyan)" />
                    Recent Intelligence Feed
                  </h2>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                    {recentActivity.map((act) => (
                      <div key={act.id} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-cyan)', marginTop: '0.35rem' }} />
                        <div>
                          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#F8FAFC' }}>{act.title}</div>
                          <div style={{ fontSize: '0.725rem', color: '#94A3B8' }}>{act.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </div>
          </>
        )}

        {/* Modal detail */}
        {selectedRec && (
          <FundingDetailModal
            recommendation={selectedRec}
            onClose={() => setSelectedRec(null)}
            onFeedback={(rec, type) => handleFundingFeedback(rec.funding_id, type)}
          />
        )}

      </div>
    </AppLayout>
  )
}

export default Dashboard
