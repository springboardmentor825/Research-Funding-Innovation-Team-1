import React, { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import adminService from '../../services/admin'
import { Sparkles, Award, AlertTriangle, CheckCircle2, Bookmark, Send, ThumbsUp, XCircle, Info } from 'lucide-react'

function RecommendationMonitoring() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchMonitoringData = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminService.getRecommendations()
      setData(res)
    } catch (err) {
      console.error('Recommendation monitoring fetch error:', err)
      setError('Unable to load recommendation monitoring data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMonitoringData()
  }, [])

  const scores = data?.score_distribution || {}
  const feedback = data?.feedback_statistics || {}
  const health = data?.quality_health || {}

  return (
    <AppLayout
      title="Recommendation Engine Monitoring"
      subtitle="Track match score accuracy, user interaction signals, and recommendation health"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>

        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Evaluating recommendation engine metrics...
          </div>
        ) : error ? (
          <div className="ai-card" style={{ padding: '3rem', textAlign: 'center', color: '#EF4444' }}>
            <AlertTriangle size={36} style={{ marginBottom: '0.75rem' }} />
            <h3>Unable to Load Monitoring Data</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>{error}</p>
            <button onClick={fetchMonitoringData} className="btn-ai-primary" style={{ padding: '0.5rem 1.25rem' }}>
              Retry
            </button>
          </div>
        ) : (
          <>
            {/* System Health Alert / Insufficient Data Banner */}
            <div 
              className="ai-card" 
              style={{ 
                padding: '1.25rem 1.5rem', 
                background: health.has_sufficient_data ? 'rgba(16, 185, 129, 0.1)' : 'rgba(59, 130, 246, 0.1)',
                border: health.has_sufficient_data ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(59, 130, 246, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem'
              }}
            >
              {health.has_sufficient_data ? (
                <CheckCircle2 size={24} color="var(--accent-emerald)" style={{ flexShrink: 0 }} />
              ) : (
                <Info size={24} color="#60A5FA" style={{ flexShrink: 0 }} />
              )}
              <div>
                <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#F8FAFC', fontWeight: 700 }}>
                  {health.has_sufficient_data ? 'Recommendation Engine Status: Normal' : 'Insufficient Feedback Data Notice'}
                </h4>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {health.status_message}
                </p>
              </div>
            </div>

            {/* Top Cards: Total & Interactions */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
              
              <div className="ai-card" style={{ padding: '1.35rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>
                  Total Recommendations
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', margin: '0.5rem 0' }}>
                  {data?.total_recommendations ?? 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--accent-cyan-light)' }}>
                  Live Scored Matches
                </div>
              </div>

              <div className="ai-card" style={{ padding: '1.35rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>
                  User Feedback Signals
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', margin: '0.5rem 0' }}>
                  {feedback.total_interactions ?? 0}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--accent-emerald)' }}>
                  Saved, Applied & Relevant
                </div>
              </div>

              <div className="ai-card" style={{ padding: '1.35rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase' }}>
                  Quality / Precision Signal
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', margin: '0.5rem 0' }}>
                  {typeof health.precision_estimate === 'number' ? `${health.precision_estimate}%` : 'N/A'}
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                  {health.has_sufficient_data ? 'Based on real user interactions' : 'Insufficient feedback data'}
                </div>
              </div>

            </div>

            {/* Middle Section: Score Distribution & Feedback Breakdown */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
              
              {/* Match Score Distribution */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Sparkles size={18} color="var(--accent-cyan)" /> Match Score Distribution
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {[
                    { label: 'High Match (80% - 100%)', count: scores.high_match_80_plus || 0, color: 'var(--accent-emerald)' },
                    { label: 'Good Match (70% - 79%)', count: scores.good_match_70_79 || 0, color: 'var(--accent-cyan)' },
                    { label: 'Moderate Match (50% - 69%)', count: scores.moderate_match_50_69 || 0, color: '#FBBF24' },
                    { label: 'Low Match (< 50%)', count: scores.low_match_below_50 || 0, color: '#EF4444' }
                  ].map((sItem, sIdx) => {
                    const total = data?.total_recommendations || 1
                    const pct = Math.round((sItem.count / total) * 100)
                    return (
                      <div key={sIdx} style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem' }}>
                          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>{sItem.label}</span>
                          <span style={{ color: 'var(--text-secondary)' }}>{sItem.count} ({pct}%)</span>
                        </div>
                        <div style={{ height: '8px', width: '100%', borderRadius: '4px', background: 'rgba(30, 41, 59, 0.8)', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${pct}%`, background: sItem.color }} />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Feedback Breakdown */}
              <div className="ai-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Award size={18} color="#C084FC" /> Feedback Signals Breakdown
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  
                  <div style={{ padding: '1rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <Bookmark size={22} color="var(--accent-cyan-light)" />
                    <div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{feedback.saved || 0}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Saved Opportunities</div>
                    </div>
                  </div>

                  <div style={{ padding: '1rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <Send size={22} color="var(--accent-emerald)" />
                    <div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{feedback.applied || 0}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Applied Grants</div>
                    </div>
                  </div>

                  <div style={{ padding: '1rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <ThumbsUp size={22} color="#60A5FA" />
                    <div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{feedback.relevant || 0}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Rated Relevant</div>
                    </div>
                  </div>

                  <div style={{ padding: '1rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '10px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                    <XCircle size={22} color="#EF4444" />
                    <div>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{feedback.dismissed || 0}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Dismissed</div>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </>
        )}

      </div>
    </AppLayout>
  )
}

export default RecommendationMonitoring
