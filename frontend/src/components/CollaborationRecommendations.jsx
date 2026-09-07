// frontend/src/components/CollaborationRecommendations.jsx

import React, { useState, useEffect } from 'react'
import { getCollaboratorRecommendations } from '../services/researchIntelligence'
import { Users, Sparkles, BookOpen, Award, CheckCircle2, ChevronRight, Filter } from 'lucide-react'

const CollaborationRecommendations = ({ userId = 16 }) => {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [selectedDomain, setSelectedDomain] = useState('')

  useEffect(() => {
    fetchRecommendations()
  }, [userId, selectedDomain])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const res = await getCollaboratorRecommendations(userId, 10, selectedDomain)
      setData(res)
      setError(null)
    } catch (err) {
      console.error('Error fetching collaboration recommendations:', err)
      setError('Failed to load collaboration recommendations.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--accent-cyan-light)' }}>
        <Sparkles className="animate-spin" size={24} style={{ display: 'inline-block', marginRight: '0.5rem' }} />
        Analyzing Research Profiles & Collaboration Network...
      </div>
    )
  }

  if (error || !data) {
    return (
      <div style={{ padding: '1.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', color: '#FCA5A5' }}>
        {error || 'No recommendation data found.'}
      </div>
    )
  }

  const { researcher, collaborators, total_candidates_evaluated } = data

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Target Researcher Header & Stats */}
      <div style={{
        padding: '1.25rem 1.5rem',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <Users size={20} color="var(--accent-cyan-light)" />
            <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#F8FAFC', fontWeight: 700 }}>
              Collaboration Match Engine
            </h3>
          </div>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Evaluated <strong style={{ color: 'var(--accent-cyan-light)' }}>{total_candidates_evaluated}</strong> registered researchers against <strong>{researcher.name}</strong>'s research footprint.
          </p>
        </div>

        {/* Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="#94A3B8" />
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            style={{
              padding: '0.5rem 0.85rem',
              borderRadius: '8px',
              backgroundColor: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              color: '#F8FAFC',
              fontSize: '0.85rem'
            }}
          >
            <option value="">All Research Domains</option>
            {researcher.research_domains?.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Collaborators List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {collaborators.map((c) => {
          const isStrong = c.score >= 75
          const isMod = c.score >= 60

          return (
            <div
              key={c.researcher_id}
              style={{
                padding: '1.5rem',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                transition: 'all 0.2s ease',
                boxShadow: isStrong ? '0 0 15px rgba(6, 182, 212, 0.15)' : 'none'
              }}
            >
              {/* Top Row: Name, Designation, Match Score */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '1.15rem', color: '#F8FAFC', fontWeight: 700 }}>
                      {c.name}
                    </h4>
                    <span style={{
                      padding: '0.2rem 0.6rem',
                      borderRadius: '9999px',
                      fontSize: '0.725rem',
                      fontWeight: 700,
                      backgroundColor: isStrong ? 'rgba(6, 182, 212, 0.2)' : isMod ? 'rgba(16, 185, 129, 0.2)' : 'rgba(148, 163, 184, 0.2)',
                      color: isStrong ? 'var(--accent-cyan-light)' : isMod ? '#34D399' : '#CBD5E1',
                      border: `1px solid ${isStrong ? 'rgba(6, 182, 212, 0.4)' : isMod ? 'rgba(16, 185, 129, 0.4)' : 'rgba(148, 163, 184, 0.4)'}`
                    }}>
                      {c.match_category}
                    </span>
                  </div>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {c.designation || 'Researcher'} {c.organization ? `• ${c.organization}` : ''}
                  </p>
                </div>

                {/* Score Circle */}
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: 800,
                    color: isStrong ? 'var(--accent-cyan-light)' : isMod ? '#34D399' : '#F8FAFC'
                  }}>
                    {c.score}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Compatibility
                  </div>
                </div>
              </div>

              {/* Bio snippet */}
              {c.bio && (
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#CBD5E1', lineHeight: 1.4 }}>
                  "{c.bio}"
                </p>
              )}

              {/* Shared & Complementary Tags */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {/* Shared Technologies */}
                {c.shared_technologies.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, width: '130px' }}>Shared Tech:</span>
                    {c.shared_technologies.map((t, idx) => (
                      <span key={idx} style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        backgroundColor: 'rgba(6, 182, 212, 0.15)',
                        color: 'var(--accent-cyan-light)',
                        border: '1px solid rgba(6, 182, 212, 0.3)'
                      }}>
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                {/* Complementary Expertise */}
                {c.complementary_expertise.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '0.75rem', color: '#C084FC', fontWeight: 600, width: '130px' }}>Complementary:</span>
                    {c.complementary_expertise.map((t, idx) => (
                      <span key={idx} style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        backgroundColor: 'rgba(168, 85, 247, 0.15)',
                        color: '#E9D5FF',
                        border: '1px solid rgba(168, 85, 247, 0.3)'
                      }}>
                        + {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Evidence & Explanation Box */}
              <div style={{
                padding: '0.85rem 1rem',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <div style={{ fontSize: '0.825rem', color: '#E2E8F0', fontWeight: 500 }}>
                  <CheckCircle2 size={14} color="var(--accent-cyan-light)" style={{ display: 'inline-block', marginRight: '0.4rem' }} />
                  {c.explanation}
                </div>

                {/* Publication Evidence */}
                {c.publication_evidence?.length > 0 && (
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                    <BookOpen size={12} color="#38BDF8" />
                    <strong>Publications:</strong> {c.publication_evidence.map(p => p.title).join(' • ')}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default CollaborationRecommendations
