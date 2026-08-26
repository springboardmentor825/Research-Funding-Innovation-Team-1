import React from 'react'
import { PieChart, CheckCircle } from 'lucide-react'

function MatchBreakdownChart({ customWeights }) {
  // Default algorithm scoring weights
  const weights = customWeights || [
    { label: 'Research Domain', percentage: 30, color: 'var(--accent-cyan)' },
    { label: 'Technology Area', percentage: 20, color: '#38BDF8' },
    { label: 'Research Interests', percentage: 15, color: 'var(--accent-violet)' },
    { label: 'Keyword Overlap', percentage: 15, color: '#A855F7' },
    { label: 'Publication Signals', percentage: 10, color: 'var(--accent-emerald)' },
    { label: 'Patent Domains', percentage: 5, color: '#F59E0B' },
    { label: 'Deadline & Eligibility', percentage: 5, color: '#64748B' },
  ]

  return (
    <div className="ai-card" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <PieChart size={18} color="var(--accent-cyan-light)" />
          Match Breakdown
        </h3>
        <span style={{ fontSize: '0.725rem', color: 'var(--accent-cyan-light)', background: 'rgba(6, 182, 212, 0.12)', padding: '0.2rem 0.5rem', borderRadius: '6px' }}>
          Multi-Signal Algorithm
        </span>
      </div>

      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
        Scoring algorithm weights evaluating research profile alignment.
      </p>

      {/* Progress Bars Stack */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {weights.map((w, idx) => (
          <div key={idx}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.35rem' }}>
              <span style={{ color: '#E2E8F0', fontWeight: 500 }}>{w.label}</span>
              <span style={{ color: w.color, fontWeight: 700 }}>{w.percentage}%</span>
            </div>
            
            <div style={{ width: '100%', height: '7px', background: 'rgba(30, 41, 59, 0.8)', borderRadius: '9999px', overflow: 'hidden' }}>
              <div 
                style={{ 
                  width: `${w.percentage}%`, 
                  height: '100%', 
                  backgroundColor: w.color,
                  borderRadius: '9999px',
                  boxShadow: `0 0 8px ${w.color}`
                }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default MatchBreakdownChart
