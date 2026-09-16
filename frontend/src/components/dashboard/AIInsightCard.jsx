import React from 'react'
import { Sparkles, BrainCircuit } from 'lucide-react'

function AIInsightCard({ topRecommendation }) {
  const reasonText = topRecommendation?.reason 
    ? topRecommendation.reason
    : 'Your profile exhibits strong alignment with Artificial Intelligence, RAG, NLP, and LLM grants based on authored publications and patent data.'

  const topScore = topRecommendation?.match_score || 94
  const topTitle = topRecommendation?.title || 'AI Research Grant 2026'

  return (
    <div 
      className="ai-card glow-animation" 
      style={{ 
        padding: '1.5rem',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
        border: '1px solid var(--border-glow)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.85rem' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-violet) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
        }}>
          <BrainCircuit size={20} color="#FFFFFF" />
        </div>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
            AI Recommendation Insight
          </h3>
          <span style={{ fontSize: '0.725rem', color: 'var(--accent-cyan-light)', fontWeight: 500 }}>
            Automated Research Synthesis
          </span>
        </div>
      </div>

      <div style={{ 
        fontSize: '0.9rem', 
        color: '#E2E8F0', 
        lineHeight: 1.5, 
        padding: '0.85rem 1rem', 
        borderRadius: '10px', 
        background: 'rgba(6, 182, 212, 0.08)',
        borderLeft: '3px solid var(--accent-cyan)'
      }}>
        "Your profile has a <strong>{topScore}% match</strong> with <em>{topTitle}</em> based on your research domain and publication portfolio."
      </div>

      <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        {reasonText}
      </div>
    </div>
  )
}

export default AIInsightCard
