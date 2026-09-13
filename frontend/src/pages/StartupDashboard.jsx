import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppLayout from '../components/layout/AppLayout'
import api from '../services/api'
import { Rocket, DollarSign, Cpu, FileText, TrendingUp, RefreshCw, ChevronRight, AlertCircle } from 'lucide-react'

function StartupDashboard() {
  const navigate = useNavigate()

  // State management for overall dashboard & individual sections
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [fundingSection, setFundingSection] = useState({ loading: true, data: [], error: '' })
  const [techSection, setTechSection] = useState({ loading: true, data: [], error: '' })
  const [patentSection, setPatentSection] = useState({ loading: true, data: [], error: '' })
  const [commSection, setCommSection] = useState({ loading: true, data: [], error: '' })

  const fetchStartupData = async () => {
    setLoading(true)
    setError('')
    setFundingSection({ loading: true, data: [], error: '' })
    setTechSection({ loading: true, data: [], error: '' })
    setPatentSection({ loading: true, data: [], error: '' })
    setCommSection({ loading: true, data: [], error: '' })

    try {
      const response = await api.get('/startup/dashboard')
      const dashData = response.data
      setData(dashData)

      const sections = dashData?.sections || {}
      
      setFundingSection({ loading: false, data: sections.funding_opportunities || [], error: '' })
      setTechSection({ loading: false, data: sections.technology_opportunities || [], error: '' })
      setPatentSection({ loading: false, data: sections.patent_intelligence || [], error: '' })
      setCommSection({ loading: false, data: sections.commercialization_insights || [], error: '' })
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Unable to load Startup Dashboard summary.'
      setError(errMsg)
      setFundingSection({ loading: false, data: [], error: 'Unable to load funding opportunities' })
      setTechSection({ loading: false, data: [], error: 'Unable to load technology opportunities' })
      setPatentSection({ loading: false, data: [], error: 'Unable to load patent insights' })
      setCommSection({ loading: false, data: [], error: 'Unable to load commercialization insights' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStartupData()
  }, [])

  if (loading) {
    return (
      <AppLayout title="Startup Founder Dashboard">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '1rem', color: 'var(--accent-cyan-light)' }}>
          <RefreshCw className="animate-spin" size={32} />
          <span style={{ fontWeight: 600 }}>Loading Startup Intelligence Dashboard...</span>
        </div>
      </AppLayout>
    )
  }

  const summary = data?.summary || {}

  return (
    <AppLayout title="Startup Founder Dashboard">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* Header & Welcome Banner */}
        <div className="ai-card" style={{
          padding: '1.75rem 2rem',
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
          border: '1px solid var(--border-glow)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
              <span className="badge-cyan" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Rocket size={14} /> Startup Founder Workspace
              </span>
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC', margin: '0 0 0.35rem 0' }}>
              Welcome, {data?.user_name || 'Founder'}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
              AI-driven commercialization, grant recommendations, and patent intelligence tailored for your venture.
            </p>
          </div>
          <button onClick={fetchStartupData} className="btn-ai-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <RefreshCw size={16} /> Refresh Insights
          </button>
        </div>

        {error && (
          <div style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#EF4444', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* SUMMARY CARDS — VISUALLY INTERACTIVE & NAVIGABLE */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
          
          {/* Card 1: Relevant Funding */}
          <div 
            onClick={() => navigate('/funding')}
            className="ai-card" 
            style={{ 
              padding: '1.25rem', 
              borderLeft: '4px solid #06B6D4',
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Relevant Funding Opportunities</span>
                <DollarSign size={20} color="#06B6D4" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC' }}>
                {fundingSection.error ? (
                  <span style={{ fontSize: '0.9rem', color: '#EF4444' }}>Unable to load</span>
                ) : (
                  fundingSection.data.length || summary.relevant_funding_opportunities || 0
                )}
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)' }}>Matching Startup Grants</span>
              <ChevronRight size={16} color="var(--accent-cyan-light)" />
            </div>
          </div>

          {/* Card 2: Emerging Technology */}
          <div 
            onClick={() => navigate('/innovation')}
            className="ai-card" 
            style={{ 
              padding: '1.25rem', 
              borderLeft: '4px solid #3B82F6',
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Emerging Tech Opportunities</span>
                <Cpu size={20} color="#3B82F6" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC' }}>
                {techSection.error ? (
                  <span style={{ fontSize: '0.9rem', color: '#EF4444' }}>Unable to load</span>
                ) : (
                  techSection.data.length || summary.technology_opportunities_count || 0
                )}
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: '0.75rem', color: '#60A5FA' }}>High-Growth Sectors</span>
              <ChevronRight size={16} color="#60A5FA" />
            </div>
          </div>

          {/* Card 3: Patent Intelligence */}
          <div 
            onClick={() => navigate('/patent-intelligence')}
            className="ai-card" 
            style={{ 
              padding: '1.25rem', 
              borderLeft: '4px solid #10B981',
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Patent Intelligence & IP Assets</span>
                <FileText size={20} color="#10B981" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC' }}>
                {patentSection.error ? (
                  <span style={{ fontSize: '0.9rem', color: '#EF4444' }}>Unable to load</span>
                ) : (
                  patentSection.data.length || summary.patent_insights_count || 0
                )}
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: '0.75rem', color: '#34D399' }}>Intellectual Property Assets</span>
              <ChevronRight size={16} color="#34D399" />
            </div>
          </div>

          {/* Card 4: Commercialization Insights */}
          <div 
            onClick={() => navigate('/commercialization')}
            className="ai-card" 
            style={{ 
              padding: '1.25rem', 
              borderLeft: '4px solid #F59E0B',
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Commercialization & Transfer</span>
                <TrendingUp size={20} color="#F59E0B" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F8FAFC' }}>
                {commSection.error ? (
                  <span style={{ fontSize: '0.9rem', color: '#EF4444' }}>Unable to load</span>
                ) : (
                  commSection.data.length || summary.commercialization_opportunities_count || 0
                )}
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <span style={{ fontSize: '0.75rem', color: '#FBBF24' }}>Licensing & Transfer Pathways</span>
              <ChevronRight size={16} color="#FBBF24" />
            </div>
          </div>

        </div>

        {/* SECTION 1 — FUNDING OPPORTUNITIES */}
        <div className="ai-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <DollarSign size={22} color="var(--accent-cyan-light)" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                1. Relevant Funding Opportunities
              </h2>
            </div>
            <button onClick={() => navigate('/funding')} className="btn-ai-secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
              View All Grants <ChevronRight size={14} />
            </button>
          </div>

          {fundingSection.error ? (
            <div style={{ padding: '1rem', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', fontSize: '0.875rem' }}>
              {fundingSection.error}
            </div>
          ) : fundingSection.data.length === 0 ? (
            <div style={{ padding: '1.5rem', textStyle: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              No funding opportunities currently available.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {fundingSection.data.map((opp, idx) => (
                <div key={idx} style={{
                  padding: '1.15rem',
                  borderRadius: '12px',
                  backgroundColor: '#1E293B',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.85rem'
                }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                        {opp.title}
                      </h3>
                      <span style={{
                        padding: '0.25rem 0.6rem',
                        borderRadius: '8px',
                        backgroundColor: opp.match_score >= 75 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                        color: opp.match_score >= 75 ? '#34D399' : 'var(--accent-cyan-light)',
                        fontWeight: 700,
                        fontSize: '0.8rem'
                      }}>
                        {opp.match_score}% MATCH
                      </span>
                    </div>

                    <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', margin: '0 0 0.5rem 0' }}>
                      <strong>Funder:</strong> {opp.funder} | <strong>Amount:</strong> {opp.amount_range}
                    </p>
                    
                    <p style={{ fontSize: '0.8rem', color: '#94A3B8', margin: '0 0 0.65rem 0', lineHeight: 1.35 }}>
                      {opp.reason}
                    </p>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {(opp.matched_signals || []).slice(0, 2).map((sig, sidx) => (
                        <span key={sidx} style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(6, 182, 212, 0.1)', color: 'var(--accent-cyan-light)' }}>
                          ✓ {sig}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div 
                    onClick={() => navigate('/funding')}
                    style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.65rem', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.78rem', color: 'var(--text-secondary)', cursor: 'pointer' }}
                  >
                    <span>Deadline: {opp.deadline}</span>
                    <span style={{ color: 'var(--accent-cyan-light)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      View Opportunity <ChevronRight size={14} />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* SECTION 2 — TECHNOLOGY OPPORTUNITIES */}
        <div className="ai-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Cpu size={22} color="#3B82F6" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                2. Emerging Technology Opportunities
              </h2>
            </div>
            <button onClick={() => navigate('/innovation')} className="btn-ai-secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
              Explore Tech Hub <ChevronRight size={14} />
            </button>
          </div>

          {techSection.error ? (
            <div style={{ padding: '1rem', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', fontSize: '0.875rem' }}>
              {techSection.error}
            </div>
          ) : techSection.data.length === 0 ? (
            <div style={{ padding: '1.5rem', textStyle: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              No technology opportunities currently listed.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
              {techSection.data.map((tech, idx) => (
                <div key={idx} style={{ padding: '1.15rem', borderRadius: '12px', backgroundColor: '#1E293B', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#60A5FA', fontWeight: 600 }}>{tech.domain}</span>
                    <span style={{ fontSize: '0.75rem', color: '#34D399', fontWeight: 700 }}>Growth {tech.growth_rate}</span>
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: '0 0 0.5rem 0' }}>
                    {tech.title}
                  </h3>
                  <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.35 }}>
                    {tech.description}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* SECTION 3 — PATENT INTELLIGENCE */}
        <div className="ai-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <FileText size={22} color="#10B981" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                3. Patent Intelligence & IP Assets
              </h2>
            </div>
            <button onClick={() => navigate('/patent-intelligence')} className="btn-ai-secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
              IP Analytics <ChevronRight size={14} />
            </button>
          </div>

          {patentSection.error ? (
            <div style={{ padding: '1rem', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', fontSize: '0.875rem' }}>
              {patentSection.error}
            </div>
          ) : patentSection.data.length === 0 ? (
            <div style={{ padding: '1.5rem', textStyle: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              No patent assets recorded.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {patentSection.data.map((pat, idx) => (
                <div key={idx} style={{
                  padding: '1rem 1.25rem',
                  borderRadius: '10px',
                  backgroundColor: '#1E293B',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '0.85rem'
                }}>
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F8FAFC', margin: '0 0 0.25rem 0' }}>
                      {pat.title}
                    </h4>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Patent No: <strong>{pat.patent_number}</strong> | Domain: {pat.technology_domain}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{
                      padding: '0.25rem 0.65rem',
                      borderRadius: '6px',
                      backgroundColor: pat.status === 'granted' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: pat.status === 'granted' ? '#34D399' : '#FBBF24',
                      fontSize: '0.75rem',
                      fontWeight: 700
                    }}>
                      {(pat.status || 'GRANTED').toUpperCase()}
                    </span>
                    <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>Filed: {pat.filing_date}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* SECTION 4 — COMMERCIALIZATION INSIGHTS */}
        <div className="ai-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <TrendingUp size={22} color="#F59E0B" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                4. Commercialization Insights & Transfer Pathways
              </h2>
            </div>
            <button onClick={() => navigate('/commercialization')} className="btn-ai-secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.75rem' }}>
              Transfer Pathways <ChevronRight size={14} />
            </button>
          </div>

          {commSection.error ? (
            <div style={{ padding: '1rem', borderRadius: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', fontSize: '0.875rem' }}>
              {commSection.error}
            </div>
          ) : commSection.data.length === 0 ? (
            <div style={{ padding: '1.5rem', textStyle: 'center', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              No commercialization pathways listed.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {commSection.data.map((comm, idx) => (
                <div key={idx} style={{ padding: '1.25rem', borderRadius: '12px', backgroundColor: '#1E293B', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#FBBF24', fontWeight: 700 }}>{comm.type}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)', fontWeight: 600 }}>{comm.readiness_level}</span>
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: '0 0 0.5rem 0' }}>
                    {comm.opportunity}
                  </h3>
                  <p style={{ fontSize: '0.825rem', color: '#94A3B8', margin: '0 0 0.75rem 0' }}>
                    <strong>Target Market:</strong> {comm.potential_market}
                  </p>
                  <div style={{ padding: '0.65rem 0.85rem', borderRadius: '8px', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#FCD34D', fontSize: '0.8rem', fontWeight: 600 }}>
                    👉 {comm.action}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </AppLayout>
  )
}

export default StartupDashboard
