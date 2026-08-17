import React from 'react'
import AppLayout from '../components/layout/AppLayout'
import { Lightbulb, Rocket, Users, Target, ArrowRight } from 'lucide-react'

function Innovation() {
  const projects = [
    {
      title: 'Autonomous RAG Vector Engine',
      domain: 'Artificial Intelligence',
      lead: 'Dr. Madhu Krishna',
      status: 'Active Pipeline',
      description: 'High-throughput hybrid retrieval engine integrating FAISS vector indices and SQL databases for multi-modal synthesis.'
    },
    {
      title: 'Decentralized IP Royalty Distribution',
      domain: 'Blockchain & Security',
      lead: 'Innovation Team-1',
      status: 'Prototyping',
      description: 'Smart contract framework ensuring automated micro-royalties for open science data publications.'
    },
    {
      title: 'Quantum-Resistant Encryption Pipeline',
      domain: 'Quantum Computing',
      lead: 'Cyber AI Lab',
      status: 'Grant Review',
      description: 'Post-quantum lattice cryptographic protocols for institutional research metadata defense.'
    }
  ]

  return (
    <AppLayout
      title="Innovation Hub Projects"
      subtitle="Collaborative technology pipelines, joint research tasks, and intellectual assets"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {projects.map((proj, idx) => (
            <div key={idx} className="ai-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="match-badge match-good" style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}>
                  {proj.status}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan-light)', fontWeight: 600 }}>
                  {proj.domain}
                </span>
              </div>

              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '0.35rem' }}>
                  {proj.title}
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {proj.description}
                </p>
              </div>

              <div style={{ paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                <span>Lead: <strong style={{ color: '#E2E8F0' }}>{proj.lead}</strong></span>
                <button className="btn-ai-outline" style={{ padding: '0.35rem 0.75rem', fontSize: '0.775rem' }}>
                  Explore Project
                </button>
              </div>
            </div>
          ))}
        </div>

      </div>
    </AppLayout>
  )
}

export default Innovation
