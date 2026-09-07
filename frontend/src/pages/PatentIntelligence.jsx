// frontend/src/pages/PatentIntelligence.jsx

import React, { useState, useEffect } from 'react'
import { getPatentIntelligence } from '../services/researchIntelligence'
import { Award, TrendingUp, Zap, Building, Users, Search, Activity, Sparkles } from 'lucide-react'

const PatentIntelligence = () => {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchPatentData()
  }, [])

  const fetchPatentData = async () => {
    try {
      setLoading(true)
      const res = await getPatentIntelligence()
      setData(res)
      setError(null)
    } catch (err) {
      console.error('Error fetching patent intelligence:', err)
      setError('Failed to load patent intelligence data.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--accent-cyan-light)' }}>
        <Sparkles className="animate-spin" size={28} style={{ display: 'inline-block', marginBottom: '0.5rem' }} />
        <div>Computing Patent Ecosystem Intelligence & Technology Trends...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div style={{ padding: '1.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', color: '#FCA5A5' }}>
        {error || 'No patent intelligence data found.'}
      </div>
    )
  }

  const {
    total_patents,
    active_patents,
    expired_patents,
    technology_distribution,
    trends,
    emerging_technologies,
    top_inventors,
    top_institutions
  } = data

  const filteredTrends = trends.filter(t => 
    t.technology.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div style={{ padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
          <Award size={28} color="var(--accent-cyan-light)" />
          <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800, color: '#F8FAFC' }}>
            Patent & Innovation Intelligence
          </h1>
        </div>
        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Deterministic patent analytics, emerging technology indicators, and innovation trends.
        </p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        {/* Total Patents */}
        <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Total IP Patents</span>
            <Award size={20} color="var(--accent-cyan-light)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F8FAFC', marginTop: '0.5rem' }}>
            {total_patents}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
            100% Verified DB Records
          </div>
        </div>

        {/* Active Patents */}
        <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Active Patents</span>
            <Activity size={20} color="#34D399" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#34D399', marginTop: '0.5rem' }}>
            {active_patents}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {total_patents ? round((active_patents / total_patents) * 100, 1) : 0}% of portfolio active
          </div>
        </div>

        {/* Emerging Technologies */}
        <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Emerging Techs</span>
            <Zap size={20} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#F59E0B', marginTop: '0.5rem' }}>
            {emerging_technologies.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#FBBF24', marginTop: '0.25rem' }}>
            High growth (&gt;20% YoY)
          </div>
        </div>

        {/* Top Institution */}
        <div style={{ padding: '1.25rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Top Assignee</span>
            <Building size={20} color="#C084FC" />
          </div>
          <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', marginTop: '0.5rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {top_institutions[0]?.institution || 'N/A'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#E9D5FF', marginTop: '0.25rem' }}>
            {top_institutions[0]?.patent_count || 0} patents assigned
          </div>
        </div>
      </div>

      {/* Emerging Technology Highlight Banner */}
      {emerging_technologies.length > 0 && (
        <div style={{
          padding: '1.25rem 1.5rem',
          background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.05) 100%)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#F59E0B', fontWeight: 700, fontSize: '1rem' }}>
            <Zap size={18} /> Emerging Patent Innovation Frontiers
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            {emerging_technologies.map(e => (
              <div key={e.technology} style={{
                padding: '0.5rem 0.85rem',
                borderRadius: '8px',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
                border: '1px solid rgba(245, 158, 11, 0.4)',
                fontSize: '0.85rem',
                color: '#FEF3C7',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <strong>{e.technology}</strong>
                <span style={{ fontSize: '0.75rem', color: '#FBBF24', padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(245, 158, 11, 0.2)' }}>
                  +{e.growth_rate * 100}% Growth
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid Layout for Tech Distribution & Top Inventors */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
        {/* Technology Distribution */}
        <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
            Technology Area Distribution
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {technology_distribution.map(td => (
              <div key={td.technology} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                  <span style={{ color: '#E2E8F0', fontWeight: 500 }}>{td.technology}</span>
                  <span style={{ color: 'var(--accent-cyan-light)', fontWeight: 700 }}>{td.count} ({td.percentage}%)</span>
                </div>
                <div style={{ height: '8px', backgroundColor: 'rgba(30, 41, 59, 0.8)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${td.percentage}%`, background: 'linear-gradient(90deg, var(--accent-cyan) 0%, #0284C7 100%)' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Inventors Leaderboard */}
        <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px' }}>
          <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
            Top Patent Inventors
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {top_inventors.map((inv, idx) => (
              <div key={idx} style={{
                padding: '0.75rem 1rem',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'rgba(6, 182, 212, 0.2)', color: 'var(--accent-cyan-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700 }}>
                    #{idx + 1}
                  </span>
                  <div>
                    <div style={{ fontSize: '0.9rem', color: '#F8FAFC', fontWeight: 600 }}>{inv.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{inv.primary_domain}</div>
                  </div>
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan-light)' }}>
                  {inv.patent_count} Patents
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Technology Trends Table */}
      <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#F8FAFC', fontWeight: 700 }}>
            Technology Growth Trends
          </h3>
          {/* Search bar */}
          <div style={{ position: 'relative', width: '250px' }}>
            <Search size={16} color="#94A3B8" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search technology..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.45rem 0.85rem 0.45rem 2.2rem',
                borderRadius: '8px',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                color: '#F8FAFC',
                fontSize: '0.85rem'
              }}
            />
          </div>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: '#94A3B8' }}>
                <th style={{ padding: '0.75rem' }}>Technology Area</th>
                <th style={{ padding: '0.75rem' }}>Recent Filings (2024-2026)</th>
                <th style={{ padding: '0.75rem' }}>Previous Filings</th>
                <th style={{ padding: '0.75rem' }}>Growth Rate</th>
                <th style={{ padding: '0.75rem' }}>Status Indicator</th>
              </tr>
            </thead>
            <tbody>
              {filteredTrends.map(t => (
                <tr key={t.technology} style={{ borderBottom: '1px solid rgba(30, 41, 59, 0.6)' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 600, color: '#F8FAFC' }}>{t.technology}</td>
                  <td style={{ padding: '0.75rem', color: 'var(--accent-cyan-light)' }}>{t.recent_count}</td>
                  <td style={{ padding: '0.75rem', color: '#94A3B8' }}>{t.previous_count}</td>
                  <td style={{ padding: '0.75rem', fontWeight: 700, color: t.growth_rate > 0 ? '#34D399' : '#94A3B8' }}>
                    {t.growth_rate > 0 ? `+${round(t.growth_rate * 100, 0)}%` : '0%'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {t.is_emerging ? (
                      <span style={{ padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#FBBF24', fontSize: '0.75rem', fontWeight: 700 }}>
                        ⚡ Emerging
                      </span>
                    ) : (
                      <span style={{ padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(52, 211, 153, 0.15)', color: '#34D399', fontSize: '0.75rem', fontWeight: 600 }}>
                        {t.trend}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function round(val, dec) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec)
}

export default PatentIntelligence
