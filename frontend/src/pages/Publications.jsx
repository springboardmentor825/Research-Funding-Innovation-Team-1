import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import publicationsService from '../services/publications'
import { BookOpen, Plus, Edit3, Trash2, CheckCircle2, AlertCircle, Calendar, Hash } from 'lucide-react'

function Publications() {
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form states
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [title, setTitle] = useState('')
  const [authors, setAuthors] = useState('')
  const [journal, setJournal] = useState('')
  const [pubYear, setPubYear] = useState('')
  const [doi, setDoi] = useState('')

  const fetchPublications = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await publicationsService.list()
      setPublications(data || [])
    } catch (err) {
      setError('Failed to fetch publications list.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPublications()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    const payload = {
      title,
      authors,
      journal,
      publication_year: parseInt(pubYear),
      doi: doi || null
    }

    try {
      if (editingId) {
        const updated = await publicationsService.update(editingId, payload)
        setPublications(publications.map(p => p.publication_id === editingId ? updated : p))
        setSuccess('Publication entry updated successfully!')
      } else {
        const created = await publicationsService.create(payload)
        setPublications([...publications, created])
        setSuccess('Publication entry added successfully!')
      }
      resetForm()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save publication. Make sure inputs are correct.')
    }
  }

  const handleEdit = (pub) => {
    setIsEditing(true)
    setEditingId(pub.publication_id)
    setTitle(pub.title)
    setAuthors(pub.authors)
    setJournal(pub.journal)
    setPubYear(pub.publication_year.toString())
    setDoi(pub.doi || '')
  }

  const handleDelete = async (pubId) => {
    if (!window.confirm('Are you sure you want to delete this publication?')) return
    setError('')
    setSuccess('')
    try {
      await publicationsService.delete(pubId)
      setPublications(publications.filter(p => p.publication_id !== pubId))
      setSuccess('Publication deleted successfully!')
    } catch (err) {
      setError('Failed to delete publication.')
    }
  }

  const resetForm = () => {
    setIsEditing(false)
    setEditingId(null)
    setTitle('')
    setAuthors('')
    setJournal('')
    setPubYear('')
    setDoi('')
  }

  return (
    <AppLayout
      title="Publications Portfolio"
      subtitle="Manage your authored papers, DOIs, and journal metadata"
    >
      <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Header Action Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
              Academic Publications ({publications.length})
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Publications provide semantic matching signals for your funding recommendations
            </p>
          </div>

          {!isEditing && (
            <button className="btn-ai-primary" onClick={() => setIsEditing(true)}>
              <Plus size={16} /> Register Paper
            </button>
          )}
        </div>

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

        {/* FORMS */}
        {isEditing && (
          <div className="ai-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '1.25rem' }}>
              {editingId ? 'Edit Publication Records' : 'Register New Publication Study'}
            </h3>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Paper Title *</label>
                <input className="ai-input" type="text" value={title} onChange={e => setTitle(e.target.value)} required placeholder="Optimization of RAG Retrieval Architectures" />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Authors * (Comma Separated)</label>
                <input className="ai-input" type="text" value={authors} onChange={e => setAuthors(e.target.value)} required placeholder="Jane Doe, John Smith, Bob Lee" />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Journal / Conference *</label>
                  <input className="ai-input" type="text" value={journal} onChange={e => setJournal(e.target.value)} required placeholder="IEEE Transactions on Neural Networks" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Year *</label>
                  <input className="ai-input" type="number" min="1900" max="2100" value={pubYear} onChange={e => setPubYear(e.target.value)} required placeholder="2026" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>DOI Identifier</label>
                  <input className="ai-input" type="text" value={doi} onChange={e => setDoi(e.target.value)} placeholder="10.1002/jml.204" />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button type="button" className="btn-ai-secondary" onClick={resetForm}>Cancel</button>
                <button type="submit" className="btn-ai-primary">Save Publication</button>
              </div>
            </form>
          </div>
        )}

        {/* LISTINGS */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>Loading publication registries...</div>
        ) : publications.length === 0 ? (
          <div className="ai-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <BookOpen size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Publications Registered</h3>
            <p style={{ fontSize: '0.875rem' }}>Add your publications above to boost funding recommendation match scores.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {publications.map((pub) => (
              <div key={pub.publication_id} className="ai-card" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ flexGrow: 1 }}>
                  <h3 style={{ fontSize: '1.15rem', color: '#F8FAFC', marginBottom: '0.35rem', fontWeight: 700 }}>{pub.title}</h3>
                  <p style={{ color: '#94A3B8', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    <strong>Authors:</strong> {pub.authors}
                  </p>
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', fontSize: '0.825rem', color: 'var(--accent-cyan-light)' }}>
                    <span>📚 {pub.journal}</span>
                    <span>•</span>
                    <span><Calendar size={13} style={{ verticalAlign: 'middle', marginRight: '0.2rem' }} /> {pub.publication_year}</span>
                    {pub.doi && (
                      <>
                        <span>•</span>
                        <span style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>DOI: {pub.doi}</span>
                      </>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn-ai-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }} onClick={() => handleEdit(pub)}>
                    <Edit3 size={14} /> Edit
                  </button>
                  <button 
                    onClick={() => handleDelete(pub.publication_id)}
                    style={{
                      background: 'rgba(239, 68, 68, 0.15)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#EF4444',
                      padding: '0.4rem 0.75rem',
                      borderRadius: '8px',
                      fontSize: '0.8rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem'
                    }}
                  >
                    <Trash2 size={14} /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </AppLayout>
  )
}

export default Publications
