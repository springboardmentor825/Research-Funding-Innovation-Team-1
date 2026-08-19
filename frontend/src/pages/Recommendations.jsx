import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import FundingRecommendationCard from '../components/dashboard/FundingRecommendationCard'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import { Sparkles, Filter, Bookmark, Clock, Flame, Search, History, ArrowUpDown, DollarSign } from 'lucide-react'

function Recommendations() {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState([])
  const [historyItems, setHistoryItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')
  const [selectedRec, setSelectedRec] = useState(null)
  const [savedIds, setSavedIds] = useState(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('match') // match, deadline, amount
  const [selectedFunder, setSelectedFunder] = useState('all')

  const userId = user?.id || 16

  const fetchData = async () => {
    setLoading(true)
    try {
      // 1. Fetch recommendations
      const data = await fundingService.getRecommendations(userId, 20)
      const recsList = Array.isArray(data) ? data : (data?.recommendations || [])
      setRecommendations(recsList)

      // 2. Fetch saved opportunities
      try {
        const resSaved = await fetch(`http://127.0.0.1:8000/api/funding/saved/${userId}`)
        if (resSaved.ok) {
          const savedData = await resSaved.json()
          if (Array.isArray(savedData)) {
            const sIds = new Set(savedData.map(item => item.funding_id || item.id))
            setSavedIds(sIds)
          }
        }
      } catch (err) {
        console.warn('Saved endpoint offline or empty:', err)
      }

      // 3. Fetch activity history
      try {
        const resHist = await fetch(`http://127.0.0.1:8000/api/funding/history/${userId}`)
        if (resHist.ok) {
          const histData = await resHist.json()
          setHistoryItems(histData.history || [])
        }
      } catch (err) {
        console.warn('History endpoint offline or empty:', err)
      }

    } catch (err) {
      console.error('Recommendations API error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      fetchData()
    }
  }, [userId])

  const handleFeedback = async (rec, feedbackType) => {
    try {
      const oppId = rec.funding_id || rec.id
      await fundingService.sendFeedback(userId, oppId, feedbackType)
      
      if (feedbackType === 'saved') {
        setSavedIds(prev => new Set(prev).add(oppId))
      } else if (feedbackType === 'dismissed') {
        setRecommendations(prev => (Array.isArray(prev) ? prev : []).filter(r => (r.funding_id || r.id) !== oppId))
      }

      // Refresh activity log history
      const resHist = await fetch(`http://127.0.0.1:8000/api/funding/history/${userId}`)
      if (resHist.ok) {
        const histData = await resHist.json()
        setHistoryItems(histData.history || [])
      }

    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  const safeRecs = Array.isArray(recommendations) ? recommendations : []

  // Unique funders list for filter
  const fundersList = Array.from(new Set(safeRecs.map(r => r.funder).filter(Boolean)))

  // Filter & Sort recommendations based on tab, filters & search query
  let filteredRecs = safeRecs.filter(r => {
    if (!r) return false

    // Search query match
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      const matchesText = (
        (r.title && r.title.toLowerCase().includes(q)) ||
        (r.funder && r.funder.toLowerCase().includes(q)) ||
        (r.description && r.description.toLowerCase().includes(q))
      )
      if (!matchesText) return false
    }

    // Funder filter
    if (selectedFunder !== 'all' && r.funder !== selectedFunder) {
      return false
    }

    // Tab filter
    if (activeTab === 'high') {
      return (r.match_score || 0) >= 80
    }
    if (activeTab === 'saved') {
      return savedIds.has(r.funding_id || r.id)
    }
    if (activeTab === 'closing') {
      return r.deadline_status === 'closing_soon' || (r.deadline && (r.deadline.includes('2026') || r.deadline.includes('2025')))
    }
    if (activeTab === 'new') {
      return r.status === 'recommended' || (r.match_score || 0) >= 70
    }
    if (activeTab === 'high_value') {
      return (r.amount || r.funding_amount || r.amount_range || '').includes('1,000,000') || (r.amount || r.funding_amount || r.amount_range || '').includes('500,000')
    }
    return true
  })

  // Sorting
  filteredRecs.sort((a, b) => {
    if (sortBy === 'match') {
      return (b.match_score || 0) - (a.match_score || 0)
    }
    if (sortBy === 'deadline') {
      return (a.deadline || '').localeCompare(b.deadline || '')
    }
    if (sortBy === 'amount') {
      return (b.amount_range || '').localeCompare(a.amount_range || '')
    }
    return 0
  })

  const tabs = [
    { id: 'all', label: 'Best Matches', icon: Sparkles },
    { id: 'high', label: 'Highly Relevant (≥80%)', icon: Flame },
    { id: 'closing', label: 'Closing Soon', icon: Clock },
    { id: 'new', label: 'New Opportunities', icon: Sparkles },
    { id: 'high_value', label: 'High Value Grants', icon: DollarSign },
    { id: 'saved', label: `Saved (${savedIds.size})`, icon: Bookmark },
    { id: 'history', label: `Activity History (${historyItems.length})`, icon: History },
  ]

  return (
    <AppLayout
      title="Personalized Recommendations Engine"
      subtitle="AI-ranked research funding opportunities with evidence breakdowns & feedback learning"
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.85rem',
          overflowX: 'auto'
        }}>
          {tabs.map((tab) => {
            const Icon = tab.icon
            const active = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '0.6rem 1.1rem',
                  borderRadius: '10px',
                  border: active ? '1px solid var(--border-glow)' : '1px solid transparent',
                  background: active ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                  color: active ? 'var(--accent-cyan-light)' : 'var(--text-secondary)',
                  fontWeight: active ? 700 : 500,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap'
                }}
              >
                <Icon size={16} color={active ? 'var(--accent-cyan-light)' : '#94A3B8'} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>

        {/* Smart Filters Toolbar (only if not on history tab) */}
        {activeTab !== 'history' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            background: 'rgba(30, 41, 59, 0.4)',
            padding: '0.85rem 1.25rem',
            borderRadius: '12px',
            border: '1px solid var(--border-color)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <Filter size={15} /> <span>Funder Filter:</span>
                <select
                  value={selectedFunder}
                  onChange={(e) => setSelectedFunder(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid var(--border-color)',
                    color: '#F8FAFC',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '8px',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="all">All Funders</option>
                  {fundersList.map(f => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <ArrowUpDown size={15} /> <span>Sort By:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-color)',
                  color: '#F8FAFC',
                  padding: '0.35rem 0.75rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem'
                }}
              >
                <option value="match">Match Score (High → Low)</option>
                <option value="deadline">Deadline Date</option>
                <option value="amount">Funding Value</option>
              </select>
            </div>
          </div>
        )}

        {/* Content List */}
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Analyzing profile signals & computing match recommendations...
          </div>
        ) : activeTab === 'history' ? (
          /* Activity History view */
          <div className="ai-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ color: '#F8FAFC', fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <History size={18} color="var(--accent-cyan)" /> Recommendation Activity Log
            </h3>
            {historyItems.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                No recommendation interaction history recorded yet. Interact with recommendations (Save, Apply, Dismiss) to personalize future ranking.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {historyItems.map((item, hIdx) => (
                  <div key={hIdx} style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '10px',
                    background: 'rgba(30, 41, 59, 0.5)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '0.75rem'
                  }}>
                    <div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F8FAFC' }}>{item.title}</div>
                      <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>Funder: {item.funder}</div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan-light)', fontWeight: 700 }}>
                        Score: {item.match_score}%
                      </div>
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '0.2rem 0.6rem',
                        borderRadius: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        background: item.feedback === 'saved' ? 'rgba(6, 182, 212, 0.2)' : item.feedback === 'applied' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(148, 163, 184, 0.2)',
                        color: item.feedback === 'saved' ? 'var(--accent-cyan-light)' : item.feedback === 'applied' ? '#10B981' : '#94A3B8'
                      }}>
                        {item.feedback || item.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : filteredRecs.length === 0 ? (
          <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            <Search size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Recommendations Found</h3>
            <p style={{ fontSize: '0.875rem' }}>No funding opportunities matched the selected tab filter or query.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.25rem' }}>
            {filteredRecs.map((rec, idx) => (
              <FundingRecommendationCard
                key={rec.id || idx}
                recommendation={rec}
                onViewDetails={setSelectedRec}
                onFeedback={handleFeedback}
                isSaved={savedIds.has(rec.funding_id || rec.id)}
              />
            ))}
          </div>
        )}

        {/* Detail Modal */}
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

export default Recommendations
