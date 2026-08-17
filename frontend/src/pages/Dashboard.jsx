import React, { useEffect, useState } from 'react'
import AppLayout from '../components/layout/AppLayout'
import FundingKpiCards from '../components/dashboard/FundingKpiCards'
import FundingRecommendationCard from '../components/dashboard/FundingRecommendationCard'
import MatchBreakdownChart from '../components/dashboard/MatchBreakdownChart'
import ResearchInterestTags from '../components/dashboard/ResearchInterestTags'
import AIInsightCard from '../components/dashboard/AIInsightCard'
import FundingDetailModal from '../components/dashboard/FundingDetailModal'
import { useAuth } from '../context/AuthContext'
import fundingService from '../services/funding'
import profileService from '../services/profile'
import { Sparkles, RefreshCw, AlertCircle, Search } from 'lucide-react'

function Dashboard() {
  const { user } = useAuth()
  const [recommendations, setRecommendations] = useState([])
  const [userProfile, setUserProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedRec, setSelectedRec] = useState(null)
  const [savedIds, setSavedIds] = useState(new Set())
  const [searchQuery, setSearchQuery] = useState('')

  const userId = user?.id || 16

  const loadDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch dynamic user recommendations from backend API
      const recsData = await fundingService.getRecommendations(userId, 10)
      const safeRecsList = Array.isArray(recsData) 
        ? recsData 
        : (recsData?.recommendations || [])
      
      setRecommendations(safeRecsList)

      if (recsData?.researcher_profile) {
        setUserProfile(recsData.researcher_profile)
      }

      // Fetch researcher profile
      try {
        const prof = await profileService.get()
        if (prof) setUserProfile(prof)
      } catch (pErr) {
        console.warn('Profile fetch note:', pErr)
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err)
      setError('Unable to fetch live funding recommendations. Please ensure backend service is active.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      loadDashboardData()
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

  // Ensure recommendations is safely treated as an Array
  const safeRecs = Array.isArray(recommendations) ? recommendations : []

  // Filter recommendations based on global header search query
  const filteredRecs = safeRecs.filter(r => {
    if (!r) return false
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      (r.title && r.title.toLowerCase().includes(q)) ||
      (r.funder && r.funder.toLowerCase().includes(q)) ||
      (r.description && r.description.toLowerCase().includes(q))
    )
  })

  const topRec = safeRecs.length > 0 ? safeRecs[0] : null

  return (
    <AppLayout 
      title="Funding Recommendations" 
      subtitle="Personalized for you based on your research profile"
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        
        {/* KPI Cards Section */}
        <FundingKpiCards 
          recommendations={safeRecs} 
          totalOpportunitiesCount={24}
        />

        {/* Loading State */}
        {loading && (
          <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--accent-cyan-light)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
            <RefreshCw size={32} className="glow-animation" style={{ animation: 'spin 2s linear infinite' }} />
            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>Executing Multi-Signal Recommendation Engine...</div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Matching publications, patents, and keywords using Sentence Transformers</div>
          </div>
        )}

        {/* Error Alert */}
        {error && !loading && (
          <div className="ai-card" style={{ padding: '1.25rem', border: '1px solid rgba(239, 68, 68, 0.4)', background: 'rgba(239, 68, 68, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#F8FAFC' }}>
              <AlertCircle size={20} color="#EF4444" />
              <span>{error}</span>
            </div>
            <button onClick={loadDashboardData} className="btn-ai-outline" style={{ fontSize: '0.8rem' }}>
              Retry API
            </button>
          </div>
        )}

        {/* Two-Column Dashboard Content */}
        {!loading && (
          <div className="dashboard-grid">
            
            {/* LEFT COLUMN: Top Funding Recommendations */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Sparkles size={20} color="var(--accent-cyan)" />
                  Top Funding Opportunities
                </h2>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Ranked by Similarity & Rule Signals
                </span>
              </div>

              {filteredRecs.length === 0 ? (
                <div className="ai-card" style={{ padding: '3rem 2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  <Search size={36} color="#64748B" style={{ marginBottom: '0.75rem' }} />
                  <h3 style={{ color: '#F8FAFC', marginBottom: '0.25rem' }}>No Opportunities Match Search</h3>
                  <p style={{ fontSize: '0.875rem' }}>Try clearing search keywords or updating your research profile.</p>
                </div>
              ) : (
                filteredRecs.map((rec, idx) => (
                  <FundingRecommendationCard 
                    key={rec.id || idx}
                    recommendation={rec}
                    onViewDetails={setSelectedRec}
                    onFeedback={handleFeedback}
                    isSaved={savedIds.has(rec.funding_id || rec.id)}
                  />
                ))
              )}
            </div>

            {/* RIGHT COLUMN: AI Insights, Match Breakdown, Research Interests */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              
              {/* AI Insights Card */}
              <AIInsightCard topRecommendation={topRec} />

              {/* Match Score Breakdown Visualization */}
              <MatchBreakdownChart />

              {/* Research Focus / Tags Panel */}
              <ResearchInterestTags userProfile={userProfile} />

            </div>

          </div>
        )}

        {/* Funding Detail View Modal */}
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

export default Dashboard
