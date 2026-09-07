import React, { useEffect, useState } from 'react'
import fundingService from '../services/funding'
import { Activity, ShieldCheck, TrendingUp, AlertTriangle, CheckCircle2, Clock, Target, Layers, FileText, Zap } from 'lucide-react'

export default function FundingAnalytics({ userId }) {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      try {
        const data = await fundingService.getResearcherAnalytics(userId || 16)
        setAnalytics(data)
      } catch (err) {
        console.error('Failed to load researcher analytics:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [userId])

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
        <Activity className="animate-spin" size={32} style={{ margin: '0 auto 1rem' }} />
        <p>Loading Funding Recommendation Analytics & Diagnostics...</p>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div style={{ padding: '2rem', background: '#1e293b', borderRadius: '12px', color: '#ef4444' }}>
        <AlertTriangle size={24} style={{ float: 'left', marginRight: '0.75rem' }} />
        <p style={{ margin: 0 }}>Unable to load analytics data. Please ensure the backend server is running.</p>
      </div>
    )
  }

  const {
    researcher_funding_profile: profile,
    recommendation_summary: scoreSummary,
    score_distribution: scoreDist,
    domain_analysis: domains,
    deadline_analysis: deadlines,
    activity_analysis: activity,
    evaluation,
    diagnostics,
    health_score: health,
    insights
  } = analytics

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontFamily: 'sans-serif', color: '#f8fafc' }}>
      
      {/* Top Banner KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        
        {/* KPI 1: Engine Health Score */}
        <div style={{ background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)', padding: '1.25rem', borderRadius: '12px', border: '1px solid #4338ca' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ color: '#a5b4fc', fontSize: '0.875rem', fontWeight: 600 }}>ENGINE HEALTH SCORE</span>
            <ShieldCheck size={20} color="#818cf8" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#ffffff' }}>
            {health?.score} / 100
          </div>
          <div style={{ fontSize: '0.8rem', color: '#c7d2fe', marginTop: '0.25rem' }}>
            Status: <strong>{health?.status}</strong>
          </div>
        </div>

        {/* KPI 2: Average Match Score */}
        <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 600 }}>AVERAGE MATCH SCORE</span>
            <TrendingUp size={20} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#38bdf8' }}>
            {scoreSummary?.average_score}%
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Median: {scoreSummary?.median_score}% | Max: {scoreSummary?.highest_score}%
          </div>
        </div>

        {/* KPI 3: Feedback & Saves */}
        <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 600 }}>USER SAVES & APPS</span>
            <Target size={20} color="#4ade80" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#4ade80' }}>
            {activity?.saves} Saved / {activity?.applications} Applied
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Feedback Coverage: {Math.round((activity?.feedback_coverage || 0)*100)}%
          </div>
        </div>

        {/* KPI 4: Upcoming Deadlines */}
        <div style={{ background: '#1e293b', padding: '1.25rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 600 }}>DEADLINES (30 DAYS)</span>
            <Clock size={20} color="#facc15" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#facc15' }}>
            {deadlines?.within_30_days} Urgent
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Total Eligible: {scoreSummary?.total_recommendations} grants
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>
        {['overview', 'evaluation', 'diagnostics'].map(t => (
          <button
            key={t}
            onClick={() => setActiveTab(t)}
            style={{
              padding: '0.5rem 1.25rem',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === t ? '#3b82f6' : 'transparent',
              color: activeTab === t ? '#ffffff' : '#94a3b8',
              fontWeight: 600,
              cursor: 'pointer',
              textTransform: 'capitalize'
            }}
          >
            {t === 'overview' ? 'Overview & Distribution' : t === 'evaluation' ? 'Precision@K & Quality' : 'Engine Diagnostics'}
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW & DISTRIBUTION */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          
          {/* Score Distribution Card */}
          <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 1rem', fontSize: '1.1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} color="#38bdf8" /> Score Distribution
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {scoreDist?.map(b => (
                <div key={b.range}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                    <span style={{ color: '#cbd5e1' }}>Match {b.range}%</span>
                    <span style={{ color: '#94a3b8' }}>{b.count} grants ({b.percentage}%)</span>
                  </div>
                  <div style={{ width: '100%', background: '#0f172a', borderRadius: '6px', height: '10px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${b.percentage}%`,
                        background: b.min_score >= 80 ? '#22c55e' : b.min_score >= 60 ? '#3b82f6' : '#eab308',
                        height: '100%',
                        borderRadius: '6px',
                        transition: 'width 0.4s ease'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Domain Breakdown */}
          <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 1rem', fontSize: '1.1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={18} color="#a855f7" /> Recommendations by Research Domain
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {domains?.slice(0, 5).map(d => (
                <div key={d.domain} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem', background: '#0f172a', borderRadius: '8px' }}>
                  <div>
                    <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.9rem' }}>{d.domain}</div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Avg Score: {d.average_score}%</div>
                  </div>
                  <span style={{ background: '#3b82f620', color: '#60a5fa', padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 600 }}>
                    {d.recommendation_count} grants ({d.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: PRECISION@K & QUALITY */}
      {activeTab === 'evaluation' && (
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1.1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="#facc15" /> Precision@K Evaluation & Feedback Signal Impact
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', color: '#cbd5e1', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', textAlign: 'left' }}>
                <th style={{ padding: '0.75rem' }}>Metric</th>
                <th style={{ padding: '0.75rem' }}>Evaluated Items</th>
                <th style={{ padding: '0.75rem' }}>Relevant Hits</th>
                <th style={{ padding: '0.75rem' }}>Precision Score</th>
                <th style={{ padding: '0.75rem' }}>Evaluation Status</th>
              </tr>
            </thead>
            <tbody>
              {['5', '10', '20'].map(k => {
                const item = evaluation?.[k] || {}
                return (
                  <tr key={k} style={{ borderBottom: '1px solid #0f172a' }}>
                    <td style={{ padding: '0.75rem', fontWeight: 600, color: '#f8fafc' }}>Precision@{k}</td>
                    <td style={{ padding: '0.75rem' }}>{item.evaluated_items || 0}</td>
                    <td style={{ padding: '0.75rem', color: '#4ade80' }}>{item.relevant_count || 0}</td>
                    <td style={{ padding: '0.75rem', fontWeight: 700, color: item.precision !== null ? '#38bdf8' : '#94a3b8' }}>
                      {item.precision !== null && item.precision !== undefined ? `${Math.round(item.precision * 100)}%` : 'N/A'}
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span style={{
                        padding: '0.25rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background: item.status === 'evaluated' ? '#166534' : '#334155',
                        color: item.status === 'evaluated' ? '#86efac' : '#94a3b8'
                      }}>
                        {item.status === 'evaluated' ? 'VERIFIED EVALUATED' : 'INSUFFICIENT FEEDBACK'}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* TAB 3: DIAGNOSTICS & CHECKS */}
      {activeTab === 'diagnostics' && (
        <div style={{ background: '#1e293b', padding: '1.5rem', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '1.1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldCheck size={18} color="#4ade80" /> Recommendation Engine System Diagnostics
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {diagnostics?.diagnostics_list?.map((diag, idx) => (
              <div key={idx} style={{ padding: '1rem', background: '#0f172a', borderRadius: '8px', borderLeft: `4px solid ${diag.passed ? '#22c55e' : '#ef4444'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#f8fafc' }}>
                  {diag.passed ? <CheckCircle2 size={18} color="#22c55e" /> : <AlertTriangle size={18} color="#ef4444" />}
                  {diag.check_name}
                </div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.25rem', paddingLeft: '1.6rem' }}>
                  {diag.details}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights Section */}
      {insights && insights.length > 0 && (
        <div style={{ background: '#0f172a', padding: '1.25rem', borderRadius: '12px', border: '1px solid #1e293b' }}>
          <h4 style={{ margin: '0 0 0.5rem', fontSize: '0.95rem', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={16} /> Automated Intelligence Insights
          </h4>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
            {insights.map((ins, idx) => (
              <li key={idx} style={{ marginBottom: '0.25rem' }}>{ins}</li>
            ))}
          </ul>
        </div>
      )}

    </div>
  )
}
