import React, { useState } from 'react'
import MatchScoreBadge from './MatchScoreBadge'
import { X, Sparkles, Building2, Calendar, DollarSign, Tag, Check, Bookmark, Send, ThumbsDown, ThumbsUp, Share2, AlertCircle } from 'lucide-react'

function FundingDetailModal({ recommendation, onClose, onFeedback }) {
  const [feedbackSent, setFeedbackSent] = useState(null)
  const [copied, setCopied] = useState(false)

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
    amount_range,
    eligibility,
    research_domains,
    technology_areas,
    keywords,
    research_stage,
    geographic_scope,
    funding_type,
    status,
    reason,
    matched_signals,
    unmatched_signals,
    match_breakdown
  } = recommendation

  const handleAction = async (actionType) => {
    setFeedbackSent(actionType)
    if (onFeedback) {
      await onFeedback(recommendation, actionType)
    }
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formattedAmount = amount || funding_amount || amount_range || '$50,000 – $250,000'
  const formattedDeadline = deadline || '31 Dec 2026'

  // Deadline intelligence formatting
  const calculateDeadlineBadge = (dlStr) => {
    if (!dlStr) return { text: 'Open', color: '#06B6D4', bg: 'rgba(6, 182, 212, 0.15)' }
    try {
      const dlDate = new Date(dlStr)
      const now = new Date()
      const diffDays = Math.ceil((dlDate - now) / (1000 * 60 * 60 * 24))
      if (diffDays <= 0) return { text: 'Closing Today', color: '#EF4444', bg: 'rgba(239, 68, 68, 0.2)' }
      if (diffDays <= 7) return { text: `Closing in ${diffDays} days`, color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.2)' }
      if (diffDays <= 30) return { text: 'Closing This Month', color: '#3B82F6', bg: 'rgba(59, 130, 246, 0.2)' }
      return { text: 'Open Opportunity', color: '#10B981', bg: 'rgba(16, 185, 129, 0.15)' }
    } catch {
      return { text: 'Open Opportunity', color: '#10B981', bg: 'rgba(16, 185, 129, 0.15)' }
    }
  }

  const dlBadge = calculateDeadlineBadge(deadline)

  // Signals extraction
  const signalsList = Array.isArray(matched_signals) ? matched_signals : []
  const missingSignals = Array.isArray(unmatched_signals) ? unmatched_signals : []

  // Breakdown items (default fallback if backend hasn't generated detailed breakdown)
  const breakdownItems = match_breakdown || {
    domain: Math.round((match_score * 0.25)),
    technology: Math.round((match_score * 0.20)),
    interests: Math.round((match_score * 0.15)),
    keywords: Math.round((match_score * 0.15)),
    publications: Math.round((match_score * 0.10)),
    patents: Math.round((match_score * 0.10)),
    eligibility: 5,
    deadline: 5
  }

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1100 }}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: '2rem', maxWidth: '780px', maxHeight: '90vh', overflowY: 'auto' }}>
        
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

        {/* Match Score & Deadline Intelligence Banner */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '14px',
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%)',
          border: '1px solid var(--border-glow)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>
              Personalized AI Relevance Score
            </div>
            <MatchScoreBadge score={match_score} />
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Status</div>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '12px', background: dlBadge.bg, color: dlBadge.color, display: 'inline-block', marginTop: '0.15rem' }}>
                {dlBadge.text}
              </span>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Deadline</div>
              <div style={{ fontSize: '0.9rem', color: '#F8FAFC', fontWeight: 700 }}>{formattedDeadline}</div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Grant Value</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--accent-emerald)', fontWeight: 700 }}>{formattedAmount}</div>
            </div>
          </div>
        </div>

        {/* Personalized Match Explanation */}
        {reason && (
          <div style={{
            padding: '1.1rem',
            borderRadius: '12px',
            background: 'rgba(15, 23, 42, 0.9)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            marginBottom: '1.5rem'
          }}>
            <h4 style={{ fontSize: '0.875rem', color: 'var(--accent-cyan-light)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem', margin: 0 }}>
              <Sparkles size={16} /> Personalized Match Explanation
            </h4>
            <p style={{ fontSize: '0.875rem', color: '#E2E8F0', lineHeight: 1.5, marginTop: '0.35rem' }}>
              {reason}
            </p>
          </div>
        )}

        {/* Match Breakdown Contribution Bars */}
        <div style={{
          padding: '1.25rem',
          borderRadius: '12px',
          background: 'rgba(30, 41, 59, 0.4)',
          border: '1px solid var(--border-color)',
          marginBottom: '1.5rem'
        }}>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.85rem' }}>
            Signal Weight Breakdown (Points Contribution)
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem 1.5rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Research Domain</span> <strong>{breakdownItems.domain} / 25</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.domain / 25) * 100}%`, height: '100%', background: 'var(--accent-cyan)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Technology Areas</span> <strong>{breakdownItems.technology} / 20</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.technology / 20) * 100}%`, height: '100%', background: '#8B5CF6' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Research Interests</span> <strong>{breakdownItems.interests} / 15</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.interests / 15) * 100}%`, height: '100%', background: '#3B82F6' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Keywords Overlap</span> <strong>{breakdownItems.keywords} / 15</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.keywords / 15) * 100}%`, height: '100%', background: '#06B6D4' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Publication Topics</span> <strong>{breakdownItems.publications} / 10</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.publications / 10) * 100}%`, height: '100%', background: '#10B981' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#CBD5E1', marginBottom: '0.2rem' }}>
                <span>Patent Assets</span> <strong>{breakdownItems.patents} / 10</strong>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${(breakdownItems.patents / 10) * 100}%`, height: '100%', background: '#F59E0B' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Matched vs Weak Signals */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '0.85rem', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.775rem', color: '#10B981', fontWeight: 700, marginBottom: '0.35rem' }}>
              ✓ MATCHED RESEARCH SIGNALS
            </div>
            {signalsList.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {signalsList.map((sig, sIdx) => (
                  <div key={sIdx} style={{ fontSize: '0.775rem', color: '#E2E8F0' }}>• {sig}</div>
                ))}
              </div>
            ) : <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Broad domain alignment</div>}
          </div>

          <div style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.2)', padding: '0.85rem', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.775rem', color: '#F59E0B', fontWeight: 700, marginBottom: '0.35rem' }}>
              ⚠ WEAK / UNMATCHED SIGNALS
            </div>
            {missingSignals.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {missingSignals.map((msig, mIdx) => (
                  <div key={mIdx} style={{ fontSize: '0.775rem', color: '#CBD5E1' }}>• {msig}</div>
                ))}
              </div>
            ) : <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No major criteria missing</div>}
          </div>
        </div>

        {/* Opportunity Metadata Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem', background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '12px' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Research Stage</div>
            <div style={{ fontSize: '0.85rem', color: '#F8FAFC', fontWeight: 600 }}>{research_stage || 'Applied Research & Innovation'}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Geographic Scope</div>
            <div style={{ fontSize: '0.85rem', color: '#F8FAFC', fontWeight: 600 }}>{geographic_scope || 'National / International'}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Funding Type</div>
            <div style={{ fontSize: '0.85rem', color: '#F8FAFC', fontWeight: 600 }}>{funding_type || 'Grant / Co-Funding Initiative'}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Eligibility</div>
            <div style={{ fontSize: '0.85rem', color: '#F8FAFC', fontWeight: 600 }}>{eligibility || 'Academic Researchers & R&D Labs'}</div>
          </div>
        </div>

        {/* Full Description */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>
            Full Opportunity Description
          </h4>
          <p style={{ fontSize: '0.9rem', color: '#E2E8F0', lineHeight: 1.6 }}>
            {description || 'Comprehensive funding opportunity supporting advanced research projects, technological innovation, and interdisciplinary collaboration across universities and industry R&D centers.'}
          </p>
        </div>

        {/* Action Buttons Toolbar */}
        <div style={{
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              onClick={() => handleAction('relevant')}
              style={{
                background: feedbackSent === 'relevant' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: feedbackSent === 'relevant' ? '#10B981' : '#CBD5E1',
                padding: '0.5rem 0.85rem',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <ThumbsUp size={14} /> Relevant
            </button>

            <button 
              onClick={() => handleAction('not_relevant')}
              style={{
                background: feedbackSent === 'not_relevant' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: feedbackSent === 'not_relevant' ? '#EF4444' : '#CBD5E1',
                padding: '0.5rem 0.85rem',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <ThumbsDown size={14} /> Not Relevant
            </button>

            <button 
              onClick={handleShare}
              style={{
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid var(--border-color)',
                color: '#CBD5E1',
                padding: '0.5rem 0.85rem',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem'
              }}
            >
              <Share2 size={14} /> {copied ? 'Link Copied!' : 'Share'}
            </button>
          </div>

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
                fontSize: '0.85rem'
              }}
            >
              Dismiss
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
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <Bookmark size={15} />
              <span>{feedbackSent === 'saved' ? 'Saved' : 'Save'}</span>
            </button>

            <button 
              onClick={() => handleAction('applied')}
              className="btn-ai-primary"
              style={{ padding: '0.6rem 1.25rem' }}
            >
              <Send size={15} />
              <span>{feedbackSent === 'applied' ? 'Applied!' : 'Apply Now'}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default FundingDetailModal
