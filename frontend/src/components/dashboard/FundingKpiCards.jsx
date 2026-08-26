import React from 'react'
import { Briefcase, Target, Flame, TrendingUp } from 'lucide-react'

function FundingKpiCards({ recommendations = [], totalOpportunitiesCount = 24 }) {
  const activeMatchesCount = recommendations.length
  const highMatchesCount = recommendations.filter(r => r.match_score >= 80).length
  
  const avgScore = recommendations.length > 0
    ? Math.round(recommendations.reduce((acc, curr) => acc + (curr.match_score || 0), 0) / recommendations.length)
    : 0

  const kpis = [
    {
      title: 'Funding Opportunities',
      value: totalOpportunitiesCount || 24,
      subtext: 'Active database grants',
      icon: Briefcase,
      color: 'var(--accent-cyan)',
      glow: 'rgba(6, 182, 212, 0.2)'
    },
    {
      title: 'Active Matches',
      value: activeMatchesCount,
      subtext: 'Filtered for your profile',
      icon: Target,
      color: '#38BDF8',
      glow: 'rgba(56, 189, 248, 0.2)'
    },
    {
      title: 'High Matches',
      value: highMatchesCount,
      subtext: 'Score ≥ 80% relevance',
      icon: Flame,
      color: 'var(--accent-emerald)',
      glow: 'rgba(16, 185, 129, 0.2)'
    },
    {
      title: 'Avg Match Score',
      value: `${avgScore}%`,
      subtext: 'Overall profile alignment',
      icon: TrendingUp,
      color: 'var(--accent-violet)',
      glow: 'rgba(139, 92, 246, 0.2)'
    }
  ]

  return (
    <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
      {kpis.map((kpi, idx) => {
        const Icon = kpi.icon
        return (
          <div 
            key={idx} 
            className="ai-card"
            style={{
              padding: '1.35rem 1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <div>
              <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {kpi.title}
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', margin: '0.25rem 0', letterSpacing: '-0.03em' }}>
                {kpi.value}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {kpi.subtext}
              </div>
            </div>

            <div style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: kpi.glow,
              border: `1px solid ${kpi.color}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `0 0 15px ${kpi.glow}`
            }}>
              <Icon size={24} color={kpi.color} />
            </div>
          </div>
        )
      })}
    </section>
  )
}

export default FundingKpiCards
