import React from 'react'
import { Sparkles, CheckCircle2, AlertCircle, Info } from 'lucide-react'

function MatchScoreBadge({ score }) {
  const numericScore = typeof score === 'number' ? score : parseInt(score) || 0

  let badgeClass = 'match-low'
  let label = 'Low Match'
  let Icon = Info

  if (numericScore >= 90) {
    badgeClass = 'match-high'
    label = 'High Match'
    Icon = Sparkles
  } else if (numericScore >= 75) {
    badgeClass = 'match-good'
    label = 'Good Match'
    Icon = CheckCircle2
  } else if (numericScore >= 60) {
    badgeClass = 'match-moderate'
    label = 'Moderate Match'
    Icon = AlertCircle
  }

  return (
    <div className={`match-badge ${badgeClass}`}>
      <Icon size={14} />
      <span>{numericScore}% Match</span>
      <span style={{ opacity: 0.85, fontWeight: 500, fontSize: '0.75rem', marginLeft: '0.15rem' }}>({label})</span>
    </div>
  )
}

export default MatchScoreBadge
