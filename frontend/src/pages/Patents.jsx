import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import patentsService from '../services/patents'
import { Award, Plus, Edit3, Trash2, CheckCircle2, AlertCircle, Calendar, Building, Cpu } from 'lucide-react'

function Patents() {
  const [patents, setPatents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form states matching DB columns: title, inventor, assignee, technology_domain, filing_date
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [title, setTitle] = useState('')
  const [inventor, setInventor] = useState('')
  const [assignee, setAssignee] = useState('')
  const [technologyDomain, setTechnologyDomain] = useState('')
  const [filingDate, setFilingDate] = useState('')

  const fetchPatents = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await patentsService.list()
      setPatents(data || [])
    } catch (err) {
      console.error('Fetch patents error:', err)
      setError('Failed to fetch patents list from database.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPatents()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    const payload = {
      title,
      inventor,
      assignee,
      technology_domain: technologyDomain,
      filing_date: filingDate
    }

    try {
      if (editingId) {
        const updated = await patentsService.update(editingId, payload)
        setPatents(prev => prev.map(p => p.patent_id === editingId ? updated : p))
        setSuccess('Patent record updated successfully!')
      } else {
        const created = await patentsService.create(payload)
        setPatents(prev => [...prev, created])
        setSuccess('Patent record created successfully!')
      }
      resetForm()
      // Refresh list to ensure clean DB state
      fetchPatents()
    } catch (err) {
      console.error('Save patent error:', err)
      setError(err.response?.data?.detail || 'Failed to save patent. Please ensure all required fields are filled.')
    }
  }

  const handleEdit = (pat) => {
    setIsEditing(true)
    setEditingId(pat.patent_id)
    setTitle(pat.title || '')
    setInventor(pat.inventor || '')
    setAssignee(pat.assignee || '')
    setTechnologyDomain(pat.technology_domain || '')
    setFilingDate(pat.filing_date || '')
  }

  const handleDelete = async (patId) => {
    if (!window.confirm('Are you sure you want to delete this patent record?')) return
    setError('')
    setSuccess('')
    try {
      await patentsService.delete(patId)
      setPatents(prev => prev.filter(p => p.patent_id !== patId))
      setSuccess('Patent deleted successfully!')
    } catch (err) {
      console.error('Delete patent error:', err)
      setError('Failed to delete patent record.')
    }
  }

  const resetForm = () => {
    setIsEditing(false)
    setEditingId(null)
    setTitle('')
    setInventor('')
    setAssignee('')
    setTechnologyDomain('')
    setFilingDate('')
  }

  return (
    <AppLayout
      title="Intellectual Property & Patents"
      subtitle="Track patent filings, technology domains, assignees, and inventor metadata"
    >
      <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Header Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
              Filed Intellectual Assets ({patents.length})
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Patents enhance technology domain matching in funding recommendations
            </p>
          </div>

          {!isEditing && (
            <button className="btn-ai-primary" onClick={() => setIsEditing(true)}>
              <Plus size={16} /> Register Patent
            </button>
          )}
        </div>

        {/* Notifications */}
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

        {/* Form Modal / Inline Box */}
        {isEditing && (
          <div className="ai-card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#F8FAFC', marginBottom: '1.25rem' }}>
              {editingId ? 'Edit Patent Records' : 'Register New Intellectual Property Asset'}
            </h3>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Patent Title *</label>
                <input className="ai-input" type="text" value={title} onChange={e => setTitle(e.target.value)} required placeholder="Autonomous Neural Network Vector Accelerator" />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Inventor(s) *</label>
                  <input className="ai-input" type="text" value={inventor} onChange={e => setInventor(e.target.value)} required placeholder="Dr. Jane Doe, John Smith" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Assignee / Institution *</label>
                  <input className="ai-input" type="text" value={assignee} onChange={e => setAssignee(e.target.value)} required placeholder="Stanford AI Institute / TechCorp" />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Technology Domain *</label>
                  <input className="ai-input" type="text" value={technologyDomain} onChange={e => setTechnologyDomain(e.target.value)} required placeholder="Artificial Intelligence / Quantum Computing" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>Filing Date *</label>
                  <input className="ai-input" type="date" value={filingDate} onChange={e => setFilingDate(e.target.value)} required />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button type="button" className="btn-ai-secondary" onClick={resetForm}>Cancel</button>
                <button type="submit" className="btn-ai-primary">Save Patent</button>
              </div>
            </form>
          </div>
        )}

        {/* Listings */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>Loading patent registries...</div>
        ) : patents.length === 0 ? (
          <div className="ai-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Award size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Patents Recorded</h3>
            <p style={{ fontSize: '0.875rem' }}>Add intellectual property records above to track institutional innovations.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {patents.map((pat) => (
              <div key={pat.patent_id} className="ai-card" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ flexGrow: 1 }}>
                  <h3 style={{ fontSize: '1.15rem', color: '#F8FAFC', marginBottom: '0.35rem', fontWeight: 700 }}>{pat.title}</h3>
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', fontSize: '0.875rem', color: '#94A3B8', marginBottom: '0.5rem' }}>
                    <span><strong>Inventor:</strong> {pat.inventor}</span>
                    <span><strong>Assignee:</strong> {pat.assignee}</span>
                  </div>
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', fontSize: '0.825rem', color: 'var(--accent-cyan-light)' }}>
                    <span><Cpu size={13} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} /> Domain: <strong style={{ color: '#F8FAFC' }}>{pat.technology_domain}</strong></span>
                    <span>•</span>
                    <span><Calendar size={13} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} /> Filed: {pat.filing_date}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn-ai-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }} onClick={() => handleEdit(pat)}>
                    <Edit3 size={14} /> Edit
                  </button>
                  <button 
                    onClick={() => handleDelete(pat.patent_id)}
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

export default Patents
