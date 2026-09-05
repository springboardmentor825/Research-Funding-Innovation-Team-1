import { useEffect, useRef, useState } from 'react'
import { fetchDashboardStats, fetchAllGrants } from '../services/dashboard'
import { fetchAlerts } from '../services/insights'
import StatCard from '../components/StatCard'
import GrantsTable from '../components/GrantsTable'

function fmt(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${n}`
}

export default function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null)
  const [grants, setGrants] = useState([])
  const [alerts, setAlerts] = useState(null)
  const [statsErr, setStatsErr] = useState(null)
  const [grantsErr, setGrantsErr] = useState(null)
  const [loading, setLoading] = useState(true)
  const [alertDismissed, setAlertDismissed] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    Promise.allSettled([fetchDashboardStats(), fetchAllGrants(), fetchAlerts()]).then(
      ([statsRes, grantsRes, alertsRes]) => {
        if (cancelled) return
        if (statsRes.status === 'fulfilled') setStats(statsRes.value)
        else setStatsErr('Could not load statistics. Is the backend running?')
        if (grantsRes.status === 'fulfilled') setGrants(grantsRes.value)
        else setGrantsErr('Could not load grants list.')
        if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value)
        setLoading(false)
      }
    )
    return () => { cancelled = true }
  }, [])

  const fundingTableRef = useRef(null)
  const maxAreaCount = stats?.research_areas?.[0]?.count ?? 1

  function scrollToFundingTable() {
    fundingTableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="page">
      {/* ── Deadline alert banner ── */}
      {!loading && !alertDismissed && alerts?.expiring_count > 0 && (
        <div className="dash-alert-banner" role="alert">
          <span className="dash-alert-banner__icon" aria-hidden="true">🔔</span>
          <span className="dash-alert-banner__text">
            <strong>{alerts.expiring_count} grant{alerts.expiring_count > 1 ? 's' : ''}</strong> expiring within 30 days.
            {alerts.expiring_soon[0] && (
              <> Nearest: <em>{alerts.expiring_soon[0].grant_name}</em> — {alerts.expiring_soon[0].days_left === 0 ? 'today' : `${alerts.expiring_soon[0].days_left} day${alerts.expiring_soon[0].days_left === 1 ? '' : 's'}`}.</>
            )}
          </span>
          <button
            className="btn btn--ghost btn--sm dash-alert-banner__action"
            onClick={() => onNavigate('research')}
          >
            View Alerts
          </button>
          <button
            className="dash-alert-banner__dismiss"
            onClick={() => setAlertDismissed(true)}
            aria-label="Dismiss alert"
          >
            <svg viewBox="0 0 16 16" aria-hidden="true" width="14" height="14">
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      )}

      <header className="page__header">
        <h1>Dashboard</h1>
        <p className="page__subtitle">
          Overview of the Research Funding &amp; Innovation Intelligence Platform
        </p>
      </header>

      {/* ── Summary cards ── */}
      {loading ? (
        <div className="loading-state">
          <div className="loading-dots"><span /><span /><span /></div>
          <p>Loading dashboard…</p>
        </div>
      ) : statsErr ? (
        <div className="alert alert--error" role="alert">
          <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4h1.5v4.5h-1.5zm0 5.5h1.5V12h-1.5z" fill="currentColor"/></svg>
          {statsErr}
        </div>
      ) : (
        <>
          <div className="stat-grid">
            <StatCard
              label="Total Grants"
              value={stats.total_grants}
              sub={`${stats.open_grants} open — click to view`}
              accent
              onClick={scrollToFundingTable}
            />
            <StatCard
              label="Total Funding Pool"
              value={fmt(stats.total_funding_pool)}
              sub="across open grants — click to view"
              onClick={scrollToFundingTable}
            />
            <StatCard
              label="Registered Users"
              value={stats.total_users}
              sub="platform accounts"
            />
            <StatCard
              label="Research Profiles"
              value={stats.total_profiles}
              sub="researcher profiles"
            />
          </div>

          {/* ── Research area breakdown ── */}
          {stats.research_areas.length > 0 && (
            <section className="dash-section">
              <h2 className="dash-section__title">Grants by Research Area</h2>
              <div className="area-chart">
                {stats.research_areas.map(({ area, count }) => (
                  <div key={area} className="area-bar-row">
                    <span className="area-bar-label">{area}</span>
                    <div className="area-bar-track">
                      <div
                        className="area-bar-fill"
                        style={{ width: `${(count / maxAreaCount) * 100}%` }}
                      />
                    </div>
                    <span className="area-bar-count">{count}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* ── Country breakdown ── */}
          {stats.countries.length > 0 && (
            <section className="dash-section">
              <h2 className="dash-section__title">Grants by Country / Region</h2>
              <div className="country-chips">
                {stats.countries.map(({ country, count }) => (
                  <span key={country} className="country-chip">
                    {country} <strong>{count}</strong>
                  </span>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      {/* ── Funding opportunities table ── */}
      <section className="dash-section" ref={fundingTableRef}>
        <div className="dash-section__header">
          <h2 className="dash-section__title">Funding Opportunities</h2>
          <button className="btn btn--primary btn--sm" onClick={() => onNavigate('recommendations')}>
            Find My Matches →
          </button>
        </div>
        {grantsErr ? (
          <div className="alert alert--error" role="alert">
            <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4h1.5v4.5h-1.5zm0 5.5h1.5V12h-1.5z" fill="currentColor"/></svg>
            {grantsErr}
          </div>
        ) : loading ? (
          <div className="loading-state"><div className="loading-dots"><span /><span /><span /></div></div>
        ) : (
          <GrantsTable grants={grants} />
        )}
      </section>

      {/* ── Quick match CTA ── */}
      <section className="dash-cta">
        <div className="dash-cta__body">
          <h2>Find Grants Matched to Your Research</h2>
          <p>Enter your research area and keywords to get personalised funding recommendations ranked by relevance.</p>
          <button className="btn btn--primary btn--lg" onClick={() => onNavigate('recommendations')}>
            Get Grant Recommendations
          </button>
        </div>
      </section>
    </div>
  )
}
