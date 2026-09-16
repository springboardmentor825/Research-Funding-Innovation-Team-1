import React, { useEffect, useState, useCallback, useRef } from 'react'
import AppLayout from '../components/layout/AppLayout'
import FundingRecommendationCard from '../components/dashboard/FundingRecommendationCard'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import { Search, SlidersHorizontal, RefreshCw, AlertCircle } from 'lucide-react'

const DAY = 24 * 60 * 60 * 1000
const domainsFrom = (opps) => {
  const set = new Set()
  opps.forEach(o => {
    String(o.research_domains || '').split(';').map(s => s.trim()).filter(Boolean).forEach(d => set.add(d))
  })
  return [...set].sort()
}
const deadlineStatus = (deadline) => {
  const d = new Date(deadline)
  if (isNaN(d)) return 'open'
  if (d < new Date()) return 'expired'
  if (d <= new Date(Date.now() + 60 * DAY)) return 'closing_soon'
  return 'open'
}

function Funding() {
  const { user } = useAuth()
  const [opportunities, setOpportunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedRec, setSelectedRec] = useState(null)
  const [savedIds, setSavedIds] = useState(new Set())

  const [searchQuery, setSearchQuery] = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [sortBy, setSortBy] = useState('score_desc')

  const userId = user?.id || 1
  const retryRef = useRef(null)

  const fetchOpportunities = useCallback(async (attempt = 0) => {
    setLoading(true)
    setError('')
    try {
      const [recs, directory] = await Promise.all([
        fundingService.getRecommendations(userId, 50),
        fundingService.searchFunding({})
      ])
      const recMap = new Map()
      ;(recs || []).forEach(r => recMap.set(r.funding_id ?? r.id, r))

      const combined = (Array.isArray(directory) ? directory : [])
        .map(opp => {
          const rec = recMap.get(opp.id)
          return {
            ...opp,
            funding_id: opp.id,
            match_score: rec?.match_score ?? opp.semantic_fit ?? 0,
            reason: rec?.reason || (opp.semantic_fit ? `Match score ${opp.semantic_fit}% based on broad field alignment.` : undefined),
            matched_signals: rec?.matched_signals || []
          }
        })
        .filter(o => deadlineStatus(o.deadline) !== 'expired')

      setOpportunities(combined)
    } catch (err) {
      console.error('Funding load error:', err)
      const detail = err?.message || err?.response?.data?.detail || 'Could not reach the backend.'
      if (attempt < 2) {
        retryRef.current = setTimeout(() => fetchOpportunities(attempt + 1), 3000 * (attempt + 1))
        return
      }
      setError(detail)
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    fetchOpportunities()
    return () => { if (retryRef.current) clearTimeout(retryRef.current) }
  }, [fetchOpportunities])

  const handleFeedback = async (rec, feedbackType) => {
    try {
      const oppId = rec.funding_id || rec.id
      await fundingService.sendFeedback(userId, oppId, feedbackType)
      if (feedbackType === 'saved') setSavedIds(prev => new Set(prev).add(oppId))
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  const domains = domainsFrom(opportunities)

  const processedOpps = [...opportunities]
    .filter(o => {
      if (domainFilter) {
        const list = String(o.research_domains || '').split(';').map(s => s.trim())
        if (!list.includes(domainFilter)) return false
      }
      if (statusFilter && deadlineStatus(o.deadline) !== statusFilter) return false
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        return (
          (o.title && o.title.toLowerCase().includes(q)) ||
          (o.funder && o.funder.toLowerCase().includes(q)) ||
          (o.description && o.description.toLowerCase().includes(q)) ||
          (o.research_domains && o.research_domains.toLowerCase().includes(q))
        )
      }
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'score_desc') return (b.match_score || 0) - (a.match_score || 0)
      if (sortBy === 'score_asc') return (a.match_score || 0) - (b.match_score || 0)
      if (sortBy === 'deadline') return new Date(a.deadline || 0) - new Date(b.deadline || 0)
      return 0
    })

  return (
    <AppLayout
      title="Funding Opportunities"
      subtitle="AI-ranked research grants matched to your profile, publications & patents"
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        <div className="ai-card" style={{ padding: '1.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.85rem', alignItems: 'center', flexGrow: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan-light)' }}>
              <SlidersHorizontal size={16} /> Filters:
            </div>
            <select value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)} className="ai-select" style={{ width: '200px', height: '38px', fontSize: '0.85rem' }}>
              <option value="">All Domains</option>
              {domains.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="ai-select" style={{ width: '150px', height: '38px', fontSize: '0.85rem' }}>
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="closing_soon">Closing Soon</option>
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Sort By:</span>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="ai-select" style={{ width: '170px', height: '38px', fontSize: '0.85rem' }}>
              <option value="score_desc">Match Score (High → Low)</option>
              <option value="score_asc">Match Score (Low → High)</option>
              <option value="deadline">Deadline Urgency</option>
            </select>
            <button onClick={() => fetchOpportunities()} className="btn-ai-secondary" style={{ height: '38px', padding: '0 0.85rem' }} title="Refresh list">
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading grants & ranking matches…
          </div>
        ) : error ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', maxWidth: '520px', margin: '0 auto' }}>
            <AlertCircle size={36} color="#EF4444" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.5rem' }}>Unable to Load Funding Data</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', lineHeight: 1.5 }}>{error}</p>
            <button
              onClick={() => fetchOpportunities()}
              className="btn-primary"
              style={{ padding: '0.6rem 1.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        ) : processedOpps.length === 0 ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Search size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Funding Opportunities Found</h3>
            <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>Try adjusting domain filters or clearing search criteria.</p>
            <button onClick={() => fetchOpportunities()} className="btn-ai-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
              <RefreshCw size={13} /> Refresh Data
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {processedOpps.map((opp, idx) => (
              <FundingRecommendationCard
                key={opp.id || idx}
                recommendation={opp}
                onViewDetails={setSelectedRec}
                onFeedback={handleFeedback}
                isSaved={savedIds.has(opp.funding_id || opp.id)}
              />
            ))}
          </div>
        )}

        {selectedRec && (
          <FundingDetailModal
            recommendation={selectedRec}
            onClose={() => setSelectedRec(null)}
            onFeedback={handleFeedback}
          />
        )}
      </div>
    </AppLayout>
  )
}

export default Funding