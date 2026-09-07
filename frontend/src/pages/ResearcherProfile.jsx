// frontend/src/pages/ResearcherProfile.jsx

import React, { useState, useEffect } from 'react'
import { getResearcherIntelligence, compareResearchers } from '../services/researchIntelligence'
import CollaborationRecommendations from '../components/CollaborationRecommendations'
import { User, BookOpen, Award, Sparkles, CheckCircle2, AlertCircle, ArrowUpRight, GitCompare, Activity, Layers, DollarSign } from 'lucide-react'

const ResearcherProfile = ({ userId = 16 }) => {
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview') // 'overview', 'funding', 'collaboration', 'comparison'
  
  // Comparison state
  const [compareUserId, setCompareUserId] = useState('17')
  const [comparisonData, setComparisonData] = useState(null)
  const [comparing, setComparing] = useState(false)

  useEffect(() => {
    fetchProfileData()
  }, [userId])

  const fetchProfileData = async () => {
    try {
      setLoading(true)
      const res = await getResearcherIntelligence(userId)
      setProfile(res)
      setError(null)
    } catch (err) {
      console.error('Error fetching researcher intelligence:', err)
      setError('Failed to load researcher profile intelligence.')
    } finally {
      setLoading(false)
    }
  }

  const handleRunComparison = async () => {
    if (!compareUserId) return
    try {
      setComparing(true)
      const res = await compareResearchers(userId, parseInt(compareUserId))
      setComparisonData(res)
    } catch (err) {
      console.error('Comparison error:', err)
    } finally {
      setComparing(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--accent-cyan-light)' }}>
        <Sparkles className="animate-spin" size={28} style={{ display: 'inline-block', marginBottom: '0.5rem' }} />
        <div>Building 360° Researcher Intelligence Profile...</div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div style={{ padding: '1.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', color: '#FCA5A5' }}>
        {error || 'No researcher profile data found.'}
      </div>
    )
  }

  const {
    name,
    organization,
    designation,
    bio,
    primary_domain,
    research_domains,
    technology_profile,
    research_interests,
    publication_count,
    patent_count,
    funding_intelligence,
    collaboration_intelligence,
    research_activity_score,
    profile_completeness
  } = profile

  return (
    <div style={{ padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header Profile Card */}
      <div style={{
        padding: '2rem',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid var(--border-color)',
        borderRadius: '20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: '1.5rem',
        boxShadow: '0 0 25px rgba(6, 182, 212, 0.1)'
      }}>
        {/* Left Info */}
        <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.75rem',
            fontWeight: 800,
            color: '#FFFFFF'
          }}>
            {name ? name[0] : 'R'}
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <h1 style={{ margin: 0, fontSize: '1.6rem', color: '#F8FAFC', fontWeight: 800 }}>{name}</h1>
              <span style={{
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px',
                fontSize: '0.725rem',
                fontWeight: 700,
                backgroundColor: 'rgba(6, 182, 212, 0.2)',
                color: 'var(--accent-cyan-light)',
                border: '1px solid rgba(6, 182, 212, 0.4)'
              }}>
                {primary_domain}
              </span>
            </div>

            <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              {designation || 'Researcher'} {organization ? `• ${organization}` : ''}
            </p>

            {bio && (
              <p style={{ margin: '0.75rem 0 0 0', fontSize: '0.875rem', color: '#CBD5E1', maxWidth: '700px', lineHeight: 1.4 }}>
                {bio}
              </p>
            )}
          </div>
        </div>

        {/* Right Intelligence Metrics */}
        <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
          {/* Completeness Badge */}
          <div style={{
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--border-color)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-cyan-light)' }}>
              {profile_completeness.completeness_score}%
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Profile Completeness
            </div>
          </div>

          {/* Activity Score */}
          <div style={{
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--border-color)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34D399' }}>
              {research_activity_score}/100
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Research Activity
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div style={{ display: 'flex', gap: '0.75rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
        <button
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '0.6rem 1.2rem',
            borderRadius: '8px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: activeTab === 'overview' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'overview' ? '#FFFFFF' : '#94A3B8'
          }}
        >
          Overview & Tech Profile
        </button>

        <button
          onClick={() => setActiveTab('funding')}
          style={{
            padding: '0.6rem 1.2rem',
            borderRadius: '8px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: activeTab === 'funding' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'funding' ? '#FFFFFF' : '#94A3B8'
          }}
        >
          Funding Intelligence
        </button>

        <button
          onClick={() => setActiveTab('collaboration')}
          style={{
            padding: '0.6rem 1.2rem',
            borderRadius: '8px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: activeTab === 'collaboration' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'collaboration' ? '#FFFFFF' : '#94A3B8'
          }}
        >
          Collaboration Network
        </button>

        <button
          onClick={() => setActiveTab('comparison')}
          style={{
            padding: '0.6rem 1.2rem',
            borderRadius: '8px',
            border: 'none',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            backgroundColor: activeTab === 'comparison' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'comparison' ? '#FFFFFF' : '#94A3B8'
          }}
        >
          Researcher Comparison
        </button>
      </div>

      {/* TAB 1: OVERVIEW & TECH PROFILE */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
          {/* Technology Evidence Profile */}
          <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px' }}>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
              Technology Evidence Profile
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {technology_profile.map((t) => (
                <div key={t.technology} style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <div style={{ fontSize: '0.9rem', color: '#F8FAFC', fontWeight: 600 }}>{t.technology}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                      {t.publication_count} papers • {t.patent_count} patents
                    </div>
                  </div>
                  <span style={{
                    padding: '0.2rem 0.55rem',
                    borderRadius: '6px',
                    fontSize: '0.725rem',
                    fontWeight: 700,
                    backgroundColor: t.prominence === 'High' ? 'rgba(6, 182, 212, 0.2)' : 'rgba(148, 163, 184, 0.2)',
                    color: t.prominence === 'High' ? 'var(--accent-cyan-light)' : '#CBD5E1'
                  }}>
                    {t.prominence} Prominence ({t.evidence_count} evidence)
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Research Portfolio Summary */}
          <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
              Research Portfolio Summary
            </h3>

            {/* Pubs & Patents counts */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <BookOpen size={20} color="#38BDF8" style={{ margin: '0 auto 0.25rem auto' }} />
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#F8FAFC' }}>{publication_count}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Publications</div>
              </div>

              <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                <Award size={20} color="#F59E0B" style={{ margin: '0 auto 0.25rem auto' }} />
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#F8FAFC' }}>{patent_count}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Patents</div>
              </div>
            </div>

            {/* Research Interests */}
            <div>
              <div style={{ fontSize: '0.85rem', color: '#94A3B8', fontWeight: 600, marginBottom: '0.5rem' }}>Research Interests:</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {research_interests?.map((i, idx) => (
                  <span key={idx} style={{ padding: '0.25rem 0.6rem', borderRadius: '6px', backgroundColor: 'rgba(30, 41, 59, 0.8)', border: '1px solid var(--border-color)', fontSize: '0.775rem', color: '#E2E8F0' }}>
                    {i}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FUNDING INTELLIGENCE */}
      {activeTab === 'funding' && (
        <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
            Funding Opportunities Fit (Integrated Parts 4 & 6)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Total Recommendations</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--accent-cyan-light)', marginTop: '0.25rem' }}>
                {funding_intelligence.total_recommendations}
              </div>
            </div>

            <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Strong Funding Matches (&ge;80%)</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#34D399', marginTop: '0.25rem' }}>
                {funding_intelligence.strong_funding_matches}
              </div>
            </div>

            <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Average Match Score</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', marginTop: '0.25rem' }}>
                {funding_intelligence.average_match_score}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: COLLABORATION NETWORK */}
      {activeTab === 'collaboration' && (
        <CollaborationRecommendations userId={userId} />
      )}

      {/* TAB 4: RESEARCHER COMPARISON */}
      {activeTab === 'comparison' && (
        <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
            Side-by-Side Researcher Comparison
          </h3>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Compare {name} with User ID:</span>
            <input
              type="number"
              value={compareUserId}
              onChange={(e) => setCompareUserId(e.target.value)}
              style={{
                width: '100px',
                padding: '0.45rem 0.75rem',
                borderRadius: '8px',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                color: '#F8FAFC',
                fontSize: '0.85rem'
              }}
            />
            <button
              onClick={handleRunComparison}
              disabled={comparing}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                backgroundColor: 'var(--accent-cyan)',
                border: 'none',
                color: '#FFFFFF',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {comparing ? 'Comparing...' : 'Run Comparison'}
            </button>
          </div>

          {comparisonData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  <h4 style={{ margin: 0, color: 'var(--accent-cyan-light)' }}>{comparisonData.researcher1.name}</h4>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{comparisonData.researcher1.organization}</p>
                  <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#F8FAFC' }}>Activity Score: {comparisonData.researcher1.activity_score}</div>
                </div>

                <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  <h4 style={{ margin: 0, color: '#34D399' }}>{comparisonData.researcher2.name}</h4>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{comparisonData.researcher2.organization}</p>
                  <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#F8FAFC' }}>Activity Score: {comparisonData.researcher2.activity_score}</div>
                </div>
              </div>

              {/* Shared Techs */}
              <div style={{ padding: '1rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.85rem', color: '#94A3B8', fontWeight: 600 }}>Shared Technologies:</div>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                  {comparisonData.shared_technologies.map(t => (
                    <span key={t} style={{ padding: '0.2rem 0.5rem', borderRadius: '6px', background: 'rgba(6, 182, 212, 0.2)', color: 'var(--accent-cyan-light)', fontSize: '0.8rem' }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResearcherProfile
