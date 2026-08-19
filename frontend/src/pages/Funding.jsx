import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import FundingRecommendationCard from '../components/dashboard/FundingRecommendationCard'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import { Search, Filter, SlidersHorizontal, RefreshCw } from 'lucide-react'

function Funding() {
  const { user } = useAuth()
  const [opportunities, setOpportunities] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedRec, setSelectedRec] = useState(null)
  const [savedIds, setSavedIds] = useState(new Set())
  
  // Filter States
  const [searchQuery, setSearchQuery] = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('open')
  const [sortBy, setSortBy] = useState('score_desc')

  const userId = user?.id || 16

  const fetchOpportunities = async () => {
    setLoading(true)
    try {
      const filters = { user_id: userId }
      if (domainFilter) filters.domain = domainFilter
      if (statusFilter) filters.status = statusFilter
      if (searchQuery) filters.query = searchQuery

      const data = await fundingService.searchFunding(filters)
      setOpportunities(data || [])
    } catch (err) {
      console.error('Search funding API error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOpportunities()
  }, [domainFilter, statusFilter])

  const handleFeedback = async (rec, feedbackType) => {
    try {
      const oppId = rec.funding_id || rec.id
      await fundingService.sendFeedback(user?.id || 16, oppId, feedbackType)
      if (feedbackType === 'saved') {
        setSavedIds(prev => new Set(prev).add(oppId))
      }
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  // Local sorting & search text filtering
  const processedOpps = [...opportunities]
    .filter(o => {
      if (!searchQuery) return true
      const q = searchQuery.toLowerCase()
      return (
        (o.title && o.title.toLowerCase().includes(q)) ||
        (o.funder && o.funder.toLowerCase().includes(q)) ||
        (o.description && o.description.toLowerCase().includes(q)) ||
        (o.research_domains && o.research_domains.toLowerCase().includes(q))
      )
    })
    .sort((a, b) => {
      if (sortBy === 'score_desc') return (b.match_score || 0) - (a.match_score || 0)
      if (sortBy === 'score_asc') return (a.match_score || 0) - (b.match_score || 0)
      if (sortBy === 'deadline') return new Date(a.deadline || 0) - new Date(b.deadline || 0)
      return 0
    })

  return (
    <AppLayout
      title="Funding Opportunities Directory"
      subtitle="Explore institutional, corporate, and federal research grants"
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Filter Controls Bar */}
        <div className="ai-card" style={{ padding: '1.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.85rem', alignItems: 'center', flexGrow: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan-light)' }}>
              <SlidersHorizontal size={16} /> Filters:
            </div>

            {/* Domain Selector */}
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              className="ai-select"
              style={{ width: '180px', height: '38px', fontSize: '0.85rem' }}
            >
              <option value="">All Domains</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Quantum Computing">Quantum Computing</option>
              <option value="Biotechnology">Biotechnology</option>
              <option value="Renewable Energy">Renewable Energy</option>
            </select>

            {/* Status Selector */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="ai-select"
              style={{ width: '140px', height: '38px', fontSize: '0.85rem' }}
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="closing_soon">Closing Soon</option>
              <option value="active">Active</option>
            </select>
          </div>

          {/* Sort By Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Sort By:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="ai-select"
              style={{ width: '160px', height: '38px', fontSize: '0.85rem' }}
            >
              <option value="score_desc">Match Score (High → Low)</option>
              <option value="score_asc">Match Score (Low → High)</option>
              <option value="deadline">Deadline Urgency</option>
            </select>

            <button onClick={fetchOpportunities} className="btn-ai-secondary" style={{ height: '38px', padding: '0 0.85rem' }}>
              <RefreshCw size={14} />
            </button>
          </div>

        </div>

        {/* Opportunities List */}
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Searching database grants...
          </div>
        ) : processedOpps.length === 0 ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Search size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Funding Opportunities Found</h3>
            <p style={{ fontSize: '0.875rem' }}>Try adjusting domain filters or clearing search criteria.</p>
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

        {/* Modal View */}
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
