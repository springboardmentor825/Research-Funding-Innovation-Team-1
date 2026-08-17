import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import { useAuth } from '../context/AuthContext'
import profileService from '../services/profile'
import { User, Building, Award, BookOpen, Edit3, Trash2, CheckCircle2, AlertCircle, Save } from 'lucide-react'

function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isEditing, setIsEditing] = useState(false)

  // Form states
  const [organization, setOrganization] = useState('')
  const [designation, setDesignation] = useState('')
  const [researchDomain, setResearchDomain] = useState('')
  const [technologyArea, setTechnologyArea] = useState('')
  const [researchInterests, setResearchInterests] = useState('')
  const [keywords, setKeywords] = useState('')
  const [bio, setBio] = useState('')

  const fetchProfile = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await profileService.getProfile()
      setProfile(data)
      setOrganization(data.organization || '')
      setDesignation(data.designation || '')
      setResearchDomain(data.research_domain || '')
      setTechnologyArea(data.technology_area || '')
      setResearchInterests(data.research_interests || '')
      setKeywords(data.keywords || '')
      setBio(data.bio || '')
    } catch (err) {
      if (err.response?.status === 404) {
        setProfile(null)
      } else {
        setError('Error fetching profile information.')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  const handleCreateOrUpdate = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    const payload = {
      organization,
      designation,
      research_domain: researchDomain,
      technology_area: technologyArea,
      research_interests: researchInterests || null,
      keywords: keywords || null,
      bio: bio || null,
    }

    try {
      if (profile) {
        const updated = await profileService.updateProfile(payload)
        setProfile(updated)
        setSuccess('Research Profile updated successfully!')
      } else {
        const created = await profileService.createProfile(payload)
        setProfile(created)
        setSuccess('Research Profile created successfully!')
      }
      setIsEditing(false)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile details. Make sure all values are filled.')
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you absolutely sure you want to delete your Research Profile? This action cannot be undone.')) return
    setError('')
    setSuccess('')
    try {
      await profileService.deleteProfile()
      setProfile(null)
      setOrganization('')
      setDesignation('')
      setResearchDomain('')
      setTechnologyArea('')
      setResearchInterests('')
      setKeywords('')
      setBio('')
      setSuccess('Profile deleted successfully!')
    } catch (err) {
      setError('Failed to delete profile. Please try again.')
    }
  }

  return (
    <AppLayout
      title="Research Profile Management"
      subtitle="Configure academic designation, institution, research domains, and keyword metadata"
    >
      <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {success && (
          <div className="ai-card" style={{ padding: '1rem', border: '1px solid rgba(16, 185, 129, 0.4)', background: 'rgba(16, 185, 129, 0.1)', color: '#34D399', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={18} /> {success}
          </div>
        )}

        {error && (
          <div className="ai-card" style={{ padding: '1rem', border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={18} /> {error}
          </div>
        )}

        {/* PROFILE CONTENT */}
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading research profile details...
          </div>
        ) : !profile && !isEditing ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
            <User size={48} color="var(--accent-cyan-light)" style={{ marginBottom: '1rem' }} />
            <h3 style={{ fontSize: '1.4rem', color: '#F8FAFC', marginBottom: '0.5rem' }}>Setup Your Researcher Metadata</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', maxWidth: '550px', margin: '0 auto 1.5rem auto', fontSize: '0.9rem' }}>
              Configure your primary institution, designation, research domains, and keywords so our AI engine can match federal and corporate grant schemes.
            </p>
            <button className="btn-ai-primary" onClick={() => setIsEditing(true)}>
              Initialize Profile Now
            </button>
          </div>
        ) : isEditing || !profile ? (
          <div className="ai-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Edit3 size={18} color="var(--accent-cyan)" />
              {profile ? 'Edit Researcher Metadata' : 'Configure Profile Details'}
            </h3>

            <form onSubmit={handleCreateOrUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Organization / Institution *</label>
                  <input className="ai-input" type="text" value={organization} onChange={e => setOrganization(e.target.value)} required placeholder="Stanford University / MIT" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Designation *</label>
                  <input className="ai-input" type="text" value={designation} onChange={e => setDesignation(e.target.value)} required placeholder="Lead AI Researcher / Associate Professor" />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Primary Research Domain *</label>
                  <input className="ai-input" type="text" value={researchDomain} onChange={e => setResearchDomain(e.target.value)} required placeholder="Artificial Intelligence" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Technology Area *</label>
                  <input className="ai-input" type="text" value={technologyArea} onChange={e => setTechnologyArea(e.target.value)} required placeholder="Retrieval Augmented Generation" />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Research Interests (Comma Separated)</label>
                <input className="ai-input" type="text" value={researchInterests} onChange={e => setResearchInterests(e.target.value)} placeholder="NLP, LLMs, Vector Databases, Graph Neural Networks" />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Keywords (Comma Separated)</label>
                <input className="ai-input" type="text" value={keywords} onChange={e => setKeywords(e.target.value)} placeholder="AI, RAG, NLP, search, vectors" />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Bio / Overview</label>
                <textarea className="ai-input" value={bio} onChange={e => setBio(e.target.value)} rows="4" style={{ resize: 'vertical' }} placeholder="Detail your background and ongoing research initiatives..." />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                {profile && (
                  <button type="button" className="btn-ai-secondary" onClick={() => setIsEditing(false)}>
                    Cancel
                  </button>
                )}
                <button type="submit" className="btn-ai-primary">
                  <Save size={16} /> Save Profile
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="ai-card" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
              <div>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>{profile.designation}</h3>
                <p style={{ color: 'var(--accent-cyan-light)', fontSize: '1rem', marginTop: '0.25rem', fontWeight: 500 }}>{profile.organization}</p>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn-ai-secondary" style={{ padding: '0.45rem 0.85rem', fontSize: '0.85rem' }} onClick={() => setIsEditing(true)}>
                  <Edit3 size={14} /> Edit
                </button>
                <button 
                  onClick={handleDelete}
                  style={{
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#EF4444',
                    padding: '0.45rem 0.85rem',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  <Trash2 size={14} /> Delete
                </button>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>Research Domain</h4>
                <p style={{ color: '#F8FAFC', fontWeight: 600, fontSize: '0.95rem' }}>{profile.research_domain}</p>
              </div>

              <div>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>Technology Area</h4>
                <p style={{ color: '#F8FAFC', fontWeight: 600, fontSize: '0.95rem' }}>{profile.technology_area}</p>
              </div>
            </div>

            {profile.research_interests && (
              <div>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>Research Interests</h4>
                <p style={{ color: '#E2E8F0', fontSize: '0.9rem' }}>{profile.research_interests}</p>
              </div>
            )}

            {profile.keywords && (
              <div>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>Profile Keywords</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.35rem' }}>
                  {profile.keywords.split(',').map((kw, i) => (
                    <span key={i} className="tag-pill">#{kw.trim()}</span>
                  ))}
                </div>
              </div>
            )}

            {profile.bio && (
              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.35rem' }}>About Researcher</h4>
                <p style={{ color: '#94A3B8', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>{profile.bio}</p>
              </div>
            )}
          </div>
        )}

      </div>
    </AppLayout>
  )
}

export default Profile
