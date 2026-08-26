import React, { useState } from 'react'
import MatchScoreBadge from './MatchScoreBadge'
import { X, Sparkles, Building2, Calendar, DollarSign, Tag, Check, Bookmark, Send, ThumbsDown } from 'lucide-react'

function FundingDetailModal({ recommendation, onClose, onFeedback }) {
  const [feedbackSent, setFeedbackSent] = useState(null)

  if (!recommendation) return null

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
    eligibility,
    research_domains,
    technology_areas,
    keywords,
    reason,
    matched_signals
  } = recommendation

  const handleAction = async (actionType) => {
    setFeedbackSent(actionType)
    if (onFeedback) {
      await onFeedback(recommendation, actionType)
    }
  }

  const formattedAmount = amount || funding_amount || '$50,000 – $250,000'
  const formattedDeadline = deadline || '31 Dec 2026'

  // Extract signals list
  let signalsList = []
  if (Array.isArray(matched_signals)) {
    signalsList = matched_signals
  } else if (typeof matched_signals === 'string') {
    signalsList = matched_signals.split(',').map(s => s.trim())
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: '2rem' }}>
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem' }}>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-cyan-light)', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.25rem' }}>
              <Building2 size={14} /> {funder || 'National Science Foundation'}
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#F8FAFC', margin: 0, lineHeight: 1.25 }}>
              {title}
            </h2>
          </div>

          <button 
            onClick={onClose}
            style={{
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid var(--border-color)',
              color: '#94A3B8',
              borderRadius: '10px',
              padding: '0.4rem',
              cursor: 'pointer'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Match Score Banner */}
        <div style={{
          padding: '1rem 1.25rem',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%)',
          border: '1px solid var(--border-glow)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              AI Intelligence Score
            </div>
            <div style={{ marginTop: '0.25rem' }}>
              <MatchScoreBadge score={match_score} />
            </div>
          </div>

          <div style={{ textAlign: 'right', fontSize: '0.85rem' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Deadline: <strong style={{ color: '#F8FAFC' }}>{formattedDeadline}</strong></div>
            <div style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Amount: <strong style={{ color: 'var(--accent-emerald)' }}>{formattedAmount}</strong></div>
          </div>
        </div>

        {/* Modal Body Sections */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
          
          {/* Description */}
          <div>
            <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
              Description
            </h4>
            <p style={{ fontSize: '0.925rem', color: '#E2E8F0', lineHeight: 1.6 }}>
              {description || 'Detailed grant description supporting cutting-edge research and innovation.'}
            </p>
          </div>

          {/* Why Recommended */}
          {reason && (
            <div style={{
              padding: '1rem',
              borderRadius: '12px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)'
            }}>
              <h4 style={{ fontSize: '0.9rem', color: 'var(--accent-cyan-light)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.35rem' }}>
                <Sparkles size={16} /> Why This Opportunity Matches You
              </h4>
              <p style={{ fontSize: '0.875rem', color: '#E2E8F0', lineHeight: 1.5 }}>
                {reason}
              </p>

              {signalsList.length > 0 && (
                <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.35rem' }}>
                    MATCHED RESEARCHER SIGNALS:
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {signalsList.map((sig, sIdx) => (
                      <span key={sIdx} style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '6px', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan-light)' }}>
                        ✓ {sig}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Research Domains & Tech Areas */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                Research Domains
              </h4>
              <div style={{ fontSize: '0.875rem', color: '#F8FAFC', fontWeight: 600 }}>
                {research_domains || 'Artificial Intelligence, Computer Science'}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                Technology Areas
              </h4>
              <div style={{ fontSize: '0.875rem', color: '#F8FAFC', fontWeight: 600 }}>
                {technology_areas || 'Retrieval Augmented Generation, LLMs, NLP'}
              </div>
            </div>
          </div>

          {/* Eligibility */}
          {eligibility && (
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
                Eligibility
              </h4>
              <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>
                {eligibility}
              </p>
            </div>
          )}
        </div>

        {/* Action Buttons: Save, Apply, Dismiss, Back */}
        <div style={{
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}>
          <button onClick={onClose} className="btn-ai-secondary" style={{ padding: '0.6rem 1.25rem' }}>
            Back
          </button>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              onClick={() => handleAction('dismissed')}
              style={{
                background: feedbackSent === 'dismissed' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: feedbackSent === 'dismissed' ? '#EF4444' : '#94A3B8',
                padding: '0.6rem 1rem',
                borderRadius: '10px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <ThumbsDown size={15} />
              <span>Dismiss</span>
            </button>

            <button 
              onClick={() => handleAction('saved')}
              style={{
                background: feedbackSent === 'saved' ? 'rgba(6, 182, 212, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: feedbackSent === 'saved' ? 'var(--accent-cyan-light)' : '#F8FAFC',
                padding: '0.6rem 1rem',
                borderRadius: '10px',
                cursor: 'pointer',
                fontWeight: 600,
                fontSize: '0.875rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <Bookmark size={15} />
              <span>{feedbackSent === 'saved' ? 'Saved!' : 'Save'}</span>
            </button>

            <button 
              onClick={() => handleAction('applied')}
              className="btn-ai-primary"
              style={{ padding: '0.6rem 1.25rem' }}
            >
              <Send size={15} />
              <span>{feedbackSent === 'applied' ? 'Application Initiated!' : 'Apply Now'}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default FundingDetailModal
