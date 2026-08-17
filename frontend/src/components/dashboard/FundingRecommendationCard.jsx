import React from 'react'
import MatchScoreBadge from './MatchScoreBadge'
import { Calendar, DollarSign, Building2, ChevronRight, Sparkles, Bookmark, Check } from 'lucide-react'

function FundingRecommendationCard({ recommendation, onViewDetails, onFeedback, isSaved }) {
  const {
    id,
    funding_id,
    title,
    funder,
    description,
    match_score,
    deadline,
    amount,
    funding_amount,
    reason,
    matched_signals
  } = recommendation

  const formattedAmount = amount || funding_amount || '$50,000 – $250,000'
  const formattedDeadline = deadline || '31 Dec 2026'

  return (
    <div 
      className="ai-card"
      style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        position: 'relative'
      }}
    >
      {/* Header Row: Title & Match Score Badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flexGrow: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan-light)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Building2 size={13} /> {funder || 'National Science Foundation'}
            </span>
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#F8FAFC', lineHeight: 1.3, margin: 0 }}>
            {title}
          </h3>
        </div>

        <MatchScoreBadge score={match_score} />
      </div>

      {/* Description */}
      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
        {description || 'Supporting innovative AI, Retrieval Augmented Generation, NLP and LLM research initiatives.'}
      </p>

      {/* Why Recommended / Reason box */}
      {reason && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: '10px',
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-color)',
          fontSize: '0.825rem',
          color: '#E2E8F0',
          display: 'flex',
          gap: '0.65rem',
          alignItems: 'flex-start'
        }}>
          <Sparkles size={16} color="var(--accent-cyan-light)" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <strong style={{ color: 'var(--accent-cyan-light)' }}>Why Recommended: </strong>
            {reason}
          </div>
        </div>
      )}

      {/* Footer Info: Deadline, Amount, Actions */}
      <div style={{
        paddingTop: '0.85rem',
        borderTop: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Calendar size={14} color="var(--accent-cyan-light)" />
            <span>Deadline: <strong style={{ color: '#F8FAFC' }}>{formattedDeadline}</strong></span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <DollarSign size={14} color="var(--accent-emerald)" />
            <span>Amount: <strong style={{ color: 'var(--accent-emerald)' }}>{formattedAmount}</strong></span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {onFeedback && (
            <button
              onClick={() => onFeedback(recommendation, 'saved')}
              style={{
                background: isSaved ? 'rgba(6, 182, 212, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: isSaved ? 'var(--accent-cyan-light)' : '#94A3B8',
                padding: '0.45rem 0.65rem',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title={isSaved ? "Saved" : "Save Opportunity"}
            >
              <Bookmark size={15} color={isSaved ? "var(--accent-cyan-light)" : "#94A3B8"} />
            </button>
          )}

          <button
            onClick={() => onViewDetails && onViewDetails(recommendation)}
            className="btn-ai-outline"
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', padding: '0.45rem 0.85rem' }}
          >
            <span>View Details</span>
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default FundingRecommendationCard
