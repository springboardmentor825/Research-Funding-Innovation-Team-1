import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import FundingRecommendationCard from '../components/dashboard/FundingRecommendationCard'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import { Sparkles, Filter, Bookmark, Clock, Flame, Search } from 'lucide-react'

function Recommendations() {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')
  const [selectedRec, setSelectedRec] = useState(null)
  const [savedIds, setSavedIds] = useState(new Set())
  const [searchQuery, setSearchQuery] = useState('')

  const userId = user?.id || 16

  const fetchRecommendations = async () => {
    setLoading(true)
    try {
      const data = await fundingService.getRecommendations(userId, 20)
      const recsList = Array.isArray(data) ? data : (data?.recommendations || [])
      setRecommendations(recsList)
    } catch (err) {
      console.error('Recommendations API error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      fetchRecommendations()
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
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  const safeRecs = Array.isArray(recommendations) ? recommendations : []

  // Filter recommendations based on active tab & search query
  const filteredRecs = safeRecs.filter(r => {
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

    // Tab filter
    if (activeTab === 'high') {
      return (r.match_score || 0) >= 80
    }
    if (activeTab === 'saved') {
      return savedIds.has(r.funding_id || r.id)
    }
    if (activeTab === 'closing') {
      return r.deadline_status === 'closing_soon' || (r.deadline && r.deadline.includes('2026'))
    }
    return true
  })

  const tabs = [
    { id: 'all', label: 'All Recommendations', icon: Sparkles },
    { id: 'high', label: 'Highly Relevant (≥80%)', icon: Flame },
    { id: 'closing', label: 'Closing Soon', icon: Clock },
    { id: 'saved', label: `Saved (${savedIds.size})`, icon: Bookmark },
  ]

  return (
    <AppLayout
      title="Personalized Recommendations"
      subtitle="AI-ranked research opportunities matched to your profile & publications"
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

        {/* Content List */}
        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Loading personalized recommendations...
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
