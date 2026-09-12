import React, { useState } from 'react'
import MatchScoreBadge from './MatchScoreBadge'
import fundingService from '../../services/funding'
import { X, Sparkles, Building2, Calendar, DollarSign, Send, ThumbsDown, Loader2, CheckCircle2, FileText } from 'lucide-react'

function FundingDetailModal({ recommendation, onClose, onFeedback }) {
  const [feedbackSent, setFeedbackSent] = useState(null)
  const [formOpen, setFormOpen] = useState(false)
  const [researchStatement, setResearchStatement] = useState('')
  const [budgetAsk, setBudgetAsk] = useState('')
  const [applying, setApplying] = useState(false)
  const [applyError, setApplyError] = useState(null)

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

  const oppId = funding_id || id

  const handleAction = async (actionType) => {
    setFeedbackSent(actionType)
    if (onFeedback) {
      await onFeedback(recommendation, actionType)
    }
  }

  const submitApplication = async () => {
    if (!researchStatement.trim() || researchStatement.trim().length < 30) {
      setApplyError('Please write a research statement of at least 30 characters.')
      return
    }
    setApplying(true)
    setApplyError(null)
    try {
      await fundingService.submitApplication(oppId, researchStatement.trim(), budgetAsk.trim())
      setFeedbackSent('applied')
      setFormOpen(false)
      setApplying(false)
      if (onFeedback) {
        await onFeedback(recommendation, 'applied')
      }
    } catch (err) {
      setApplying(false)
      const detail = err?.response?.data?.detail || 'Could not submit your application. Please try again.'
      if (typeof detail === 'string' && detail.includes('already applied')) {
        setFeedbackSent('applied')
        setFormOpen(false)
      } else {
        setApplyError(detail)
      }
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem' }}>

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

        {/* Application Form / Status */}
        {feedbackSent === 'applied' && !applyError ? (
          <div style={{
            padding: '1rem 1.25rem', borderRadius: '12px', marginBottom: '1.5rem',
            background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.35)',
            display: 'flex', alignItems: 'center', gap: '0.6rem'
          }}>
            <CheckCircle2 size={18} color="#10b981" />
            <span style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: 600 }}>
              Application submitted successfully. Track it on your dashboard.
            </span>
          </div>
        ) : formOpen ? (
          <div style={{
            padding: '1.25rem', borderRadius: '12px', marginBottom: '1.5rem',
            background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-color)'
          }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.4rem', margin: '0 0 0.9rem 0' }}>
              <FileText size={16} color="var(--accent-cyan-light)" /> Submit Your Application
            </h4>

            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.35rem' }}>
              RESEARCH STATEMENT *
            </label>
            <textarea
              value={researchStatement}
              onChange={(e) => setResearchStatement(e.target.value)}
              placeholder="Briefly describe your project, objectives, and how it aligns with this funding opportunity…"
              rows={5}
              style={{
                width: '100%', boxSizing: 'border-box', resize: 'vertical',
                background: 'rgba(30, 41, 59, 0.8)', color: '#E2E8F0',
                border: applyError ? '1px solid #ef4444' : '1px solid var(--border-color)',
                borderRadius: '10px', padding: '0.7rem 0.9rem', fontSize: '0.875rem', lineHeight: 1.5,
                outline: 'none'
              }}
            />

            <div style={{ marginTop: '0.9rem', display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.75rem', alignItems: 'end' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.35rem' }}>
                  BUDGET ASK
                </label>
                <input
                  value={budgetAsk}
                  onChange={(e) => setBudgetAsk(e.target.value)}
                  placeholder="e.g. $120,000"
                  style={{
                    width: '100%', boxSizing: 'border-box',
                    background: 'rgba(30, 41, 59, 0.8)', color: '#E2E8F0',
                    border: '1px solid var(--border-color)', borderRadius: '10px',
                    padding: '0.6rem 0.9rem', fontSize: '0.875rem', outline: 'none'
                  }}
                />
              </div>
              <button
                className="btn-ai-primary"
                onClick={submitApplication}
                disabled={applying}
                style={{ padding: '0.6rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                {applying ? <><Loader2 size={15} /> Submitting…</> : <><Send size={15} /> Submit Application</>}
              </button>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginTop: '0.75rem' }}>
              {applyError && <span style={{ fontSize: '0.8rem', color: '#ef4444', flex: 1 }}>{applyError}</span>}
              {!applyError && <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', flex: 1 }}>Minimum 30 characters in your statement.</span>}
              <button
                onClick={() => { setFormOpen(false); setApplyError(null) }}
                style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : null}

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
              <Send size={15} />
              <span>{feedbackSent === 'saved' ? 'Saved!' : 'Save'}</span>
            </button>

            {feedbackSent === 'applied' ? (
              <button
                className="btn-ai-primary"
                disabled
                style={{ padding: '0.6rem 1.25rem', opacity: 0.85, cursor: 'default' }}
              >
                <CheckCircle2 size={15} />
                <span>Applied</span>
              </button>
            ) : (
              <button
                onClick={() => setFormOpen(true)}
                className="btn-ai-primary"
                style={{ padding: '0.6rem 1.25rem' }}
              >
                <Send size={15} />
                <span>Apply Now</span>
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

export default FundingDetailModal