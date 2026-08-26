import React from 'react'
import { Tag, Sparkles } from 'lucide-react'

function ResearchInterestTags({ userProfile, defaultInterests }) {
  // Extract interests from user profile or fallback to defaults
  let tags = []

  if (userProfile) {
    if (userProfile.research_interests) {
      tags = userProfile.research_interests.split(',').map(s => s.trim())
    } else if (userProfile.keywords) {
      tags = userProfile.keywords.split(',').map(s => s.trim())
    } else if (userProfile.research_domain) {
      tags = [userProfile.research_domain, userProfile.technology_area].filter(Boolean)
    }
  }

  if (tags.length === 0) {
    tags = defaultInterests || [
      'Artificial Intelligence',
      'RAG',
      'NLP',
      'LLMs',
      'Information Retrieval',
      'Vector Search',
      'Knowledge Graphs'
    ]
  }

  return (
    <div className="ai-card" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Tag size={18} color="var(--accent-cyan-light)" />
          Research Focus & Tags
        </h3>
        <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
          From Profile
        </span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {tags.map((tag, idx) => (
          <span key={idx} className="tag-pill">
            #{tag}
          </span>
        ))}
      </div>
    </div>
  )
}

export default ResearchInterestTags
