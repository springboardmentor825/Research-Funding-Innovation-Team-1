import { useEffect, useRef, useState } from 'react'
import { fetchDashboardStats, fetchAllGrants } from '../services/dashboard'
import {
  fetchResearcherOverview,
  fetchPatentInsights,
  fetchPublicationInsights,
  fetchAlerts,
} from '../services/insights'
import { matchGrants } from '../services/grants'
import StatCard from '../components/StatCard'
import GrantCard from '../components/GrantCard'
import SectionCard from '../components/SectionCard'

/* ── helpers ─────────────────────────────────────────────── */
function fmt(n) {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${n}`
}

function daysLabel(n) {
  if (n === 0) return 'Today'
  if (n === 1) return '1 day left'
  return `${n} days left`
}

function LoadingDots() {
  return (
    <div className="loading-state">
      <div className="loading-dots"><span /><span /><span /></div>
    </div>
  )
}

function ErrorBanner({ msg }) {
  return (
    <div className="alert alert--error" role="alert">
      <svg viewBox="0 0 16 16" aria-hidden="true">
        <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4h1.5v4.5h-1.5zm0 5.5h1.5V12h-1.5z" fill="currentColor" />
      </svg>
      {msg}
    </div>
  )
}

/* ── inline grant-match form (reuses existing service) ───── */
const EMPTY_FORM = { research_area: '', keywords: '', country: '', eligibility: '' }

function FundingRecommendationsSection() {
  const [form, setForm] = useState(EMPTY_FORM)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    const keywords = form.keywords.split(',').map(k => k.trim()).filter(Boolean)
    if (!form.research_area.trim()) { setError('Research area is required.'); return }
    if (!keywords.length) { setError('Enter at least one keyword.'); return }
    setLoading(true)
    try {
      const data = await matchGrants({
        research_area: form.research_area.trim(),
        keywords,
        ...(form.country.trim() && { country: form.country.trim() }),
        ...(form.eligibility.trim() && { eligibility: form.eligibility.trim() }),
      })
      setResults(data.matches ?? [])
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SectionCard title="Funding Recommendations">
      <div className="search-section" style={{ marginBottom: '1.25rem' }}>
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="rd_research_area">
                Research Area <span className="required">*</span>
              </label>
              <input
                id="rd_research_area" name="research_area" type="text"
                placeholder="e.g. Artificial Intelligence"
                value={form.research_area} onChange={handleChange} required
              />
            </div>
            <div className="form-field">
              <label htmlFor="rd_keywords">
                Keywords <span className="required">*</span>
                <span className="field-hint"> — comma-separated</span>
              </label>
              <input
                id="rd_keywords" name="keywords" type="text"
                placeholder="e.g. machine learning, NLP"
                value={form.keywords} onChange={handleChange} required
              />
            </div>
            <div className="form-field">
              <label htmlFor="rd_country">Country</label>
              <input
                id="rd_country" name="country" type="text"
                placeholder="e.g. India"
                value={form.country} onChange={handleChange}
              />
            </div>
            <div className="form-field">
              <label htmlFor="rd_eligibility">Eligibility</label>
              <input
                id="rd_eligibility" name="eligibility" type="text"
                placeholder="e.g. University Researcher"
                value={form.eligibility} onChange={handleChange}
              />
            </div>
          </div>
          {error && <ErrorBanner msg={error} />}
          <div className="form-actions">
            <button type="submit" className="btn btn--primary" disabled={loading}>
              {loading ? <><span className="spinner" aria-hidden="true" /> Searching…</> : 'Find Matching Grants'}
            </button>
            {results !== null && (
              <button type="button" className="btn btn--ghost"
                onClick={() => { setResults(null); setForm(EMPTY_FORM); setError(null) }}>
                Clear
              </button>
            )}
          </div>
        </form>
      </div>

      {loading && <LoadingDots />}

      {!loading && results !== null && (
        <div aria-live="polite">
          {results.length === 0 ? (
            <div className="empty-state">
              <p>No matching grants found. Try broader keywords.</p>
            </div>
          ) : (
            <>
              <p className="results-subtitle" style={{ marginBottom: '1rem' }}>
                {results.length} {results.length === 1 ? 'opportunity' : 'opportunities'} found — sorted by match score
              </p>
              <div className="results-grid">
                {results.map((g, i) => <GrantCard key={g.grant_id} grant={g} rank={i + 1} />)}
              </div>
            </>
          )}
        </div>
      )}
    </SectionCard>
  )
}

/* ── main page ───────────────────────────────────────────── */
export default function ResearchDashboard() {
  const [stats, setStats] = useState(null)
  const [overview, setOverview] = useState(null)
  const [patents, setPatents] = useState(null)
  const [pubs, setPubs] = useState(null)
  const [alerts, setAlerts] = useState(null)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(true)
  const [readIds, setReadIds] = useState(() => {
    try { return new Set(JSON.parse(sessionStorage.getItem('readAlerts') || '[]')) }
    catch { return new Set() }
  })

  const alertsRef = useRef(null)

  function markRead(id) {
    setReadIds(prev => {
      const next = new Set(prev)
      next.add(id)
      try { sessionStorage.setItem('readAlerts', JSON.stringify([...next])) } catch {}
      return next
    })
  }

  function markAllRead() {
    if (!alerts) return
    const ids = alerts.expiring_soon.map(a => a.grant_id)
    setReadIds(prev => {
      const next = new Set([...prev, ...ids])
      try { sessionStorage.setItem('readAlerts', JSON.stringify([...next])) } catch {}
      return next
    })
  }

  useEffect(() => {
    let cancelled = false
    Promise.allSettled([
      fetchDashboardStats(),
      fetchResearcherOverview(),
      fetchPatentInsights(),
      fetchPublicationInsights(),
      fetchAlerts(),
    ]).then(([statsR, overviewR, patentsR, pubsR, alertsR]) => {
      if (cancelled) return
      const errs = {}
      if (statsR.status === 'fulfilled') setStats(statsR.value)
      else errs.stats = 'Could not load platform stats.'
      if (overviewR.status === 'fulfilled') setOverview(overviewR.value)
      else errs.overview = 'Could not load researcher overview.'
      if (patentsR.status === 'fulfilled') setPatents(patentsR.value)
      else errs.patents = 'Could not load patent insights.'
      if (pubsR.status === 'fulfilled') setPubs(pubsR.value)
      else errs.pubs = 'Could not load publication insights.'
      if (alertsR.status === 'fulfilled') setAlerts(alertsR.value)
      else errs.alerts = 'Could not load alerts.'
      setErrors(errs)
      setLoading(false)
    })
    return () => { cancelled = true }
  }, [])

  const maxArea = stats?.research_areas?.[0]?.count ?? 1
  const maxPubYear = pubs?.by_year?.reduce((m, r) => Math.max(m, r.count), 1) ?? 1
  const unreadCount = alerts
    ? alerts.expiring_soon.filter(a => !readIds.has(a.grant_id)).length
    : 0

  return (
    <div className="page">
      <header className="page__header">
        <h1>Research Dashboard</h1>
        <p className="page__subtitle">
          Integrated overview — researcher insights, funding, patents, analytics, and alerts
        </p>
      </header>

      {/* ══════════════════════════════════════════════════════
          SECTION 1 — RESEARCHER OVERVIEW
          ══════════════════════════════════════════════════════ */}
      <SectionCard title="Researcher Overview">
        {loading ? <LoadingDots /> : errors.overview ? <ErrorBanner msg={errors.overview} /> : (
          <>
            <div className="stat-grid" style={{ marginBottom: '1.5rem' }}>
              <StatCard label="Registered Users" value={overview.total_users} sub="platform accounts" />
              <StatCard label="Research Profiles" value={overview.total_profiles} sub="active profiles" accent />
              <StatCard label="Publications" value={overview.total_publications} sub="indexed papers" />
              <StatCard label="Patents Filed" value={overview.total_patents} sub="registered patents" />
            </div>

            {overview.top_research_areas.length > 0 && (
              <div className="insight-row">
                <div className="insight-panel">
                  <p className="insight-panel__label">Top Research Areas (Profiles)</p>
                  <div className="area-chart">
                    {overview.top_research_areas.map(({ area, count }) => {
                      const max = overview.top_research_areas[0].count
                      return (
                        <div key={area} className="area-bar-row">
                          <span className="area-bar-label">{area}</span>
                          <div className="area-bar-track">
                            <div className="area-bar-fill" style={{ width: `${(count / max) * 100}%` }} />
                          </div>
                          <span className="area-bar-count">{count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {overview.designations.length > 0 && (
                  <div className="insight-panel">
                    <p className="insight-panel__label">Researcher Designations</p>
                    <div className="desig-list">
                      {overview.designations.map(({ designation, count }) => (
                        <div key={designation} className="desig-row">
                          <span className="desig-name">{designation}</span>
                          <span className="desig-count">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {overview.top_research_areas.length === 0 && overview.designations.length === 0 && (
              <p className="empty-hint" style={{ textAlign: 'center', padding: '1rem 0' }}>
                No profile data yet. Researchers can add profiles via the API.
              </p>
            )}
          </>
        )}
      </SectionCard>

      {/* ══════════════════════════════════════════════════════
          SECTION 2 — FUNDING RECOMMENDATIONS
          ══════════════════════════════════════════════════════ */}
      <FundingRecommendationsSection />

      {/* ══════════════════════════════════════════════════════
          SECTION 3 — COLLABORATION SUGGESTIONS (placeholder)
          ══════════════════════════════════════════════════════ */}
      <SectionCard title="Collaboration Suggestions">
        <div className="placeholder-section">
          <div className="placeholder-icon" aria-hidden="true">
            <svg viewBox="0 0 48 48" fill="none">
              <circle cx="16" cy="18" r="7" stroke="var(--border)" strokeWidth="2" />
              <circle cx="32" cy="18" r="7" stroke="var(--border)" strokeWidth="2" />
              <path d="M4 40c0-6.627 5.373-12 12-12h16c6.627 0 12 5.373 12 12"
                stroke="var(--border)" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <p className="placeholder-title">Collaboration Module Coming Soon</p>
          <p className="placeholder-body">
            This section will surface researcher collaboration suggestions based on shared
            research areas, co-authorship patterns, and complementary expertise.
            Integration is pending the collaboration module from the team.
          </p>
          <div className="placeholder-chips">
            <span className="placeholder-chip">Shared Research Areas</span>
            <span className="placeholder-chip">Co-authorship Network</span>
            <span className="placeholder-chip">Complementary Skills</span>
            <span className="placeholder-chip">Institution Matching</span>
          </div>
        </div>
      </SectionCard>

      {/* ══════════════════════════════════════════════════════
          SECTION 4 — PATENT / INNOVATION INSIGHTS
          ══════════════════════════════════════════════════════ */}
      <SectionCard title="Patent & Innovation Insights">
        {loading ? <LoadingDots /> : errors.patents ? <ErrorBanner msg={errors.patents} /> : (
          <>
            <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', marginBottom: '1.5rem' }}>
              <StatCard label="Total Patents" value={patents.total_patents} sub="registered" accent />
              {patents.by_status.map(({ status, count }) => (
                <StatCard key={status} label={status} value={count} sub="patents" />
              ))}
            </div>

            {patents.by_year.length > 0 && (
              <div className="insight-row">
                <div className="insight-panel" style={{ flex: 2 }}>
                  <p className="insight-panel__label">Patents Filed by Year</p>
                  <div className="area-chart">
                    {patents.by_year.map(({ year, count }) => {
                      const max = Math.max(...patents.by_year.map(r => r.count), 1)
                      return (
                        <div key={year} className="area-bar-row">
                          <span className="area-bar-label">{year}</span>
                          <div className="area-bar-track">
                            <div className="area-bar-fill" style={{ width: `${(count / max) * 100}%` }} />
                          </div>
                          <span className="area-bar-count">{count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {patents.recent_filings.length > 0 && (
                  <div className="insight-panel">
                    <p className="insight-panel__label">Recent Filings</p>
                    <div className="recent-list">
                      {patents.recent_filings.map(p => (
                        <div key={p.id} className="recent-item">
                          <span className="recent-item__title">{p.title}</span>
                          <div className="recent-item__meta">
                            {p.patent_number && <span className="tag">{p.patent_number}</span>}
                            {p.filing_date && (
                              <span className="recent-item__date">
                                {new Date(p.filing_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {patents.total_patents === 0 && (
              <p className="empty-hint" style={{ textAlign: 'center', padding: '1rem 0' }}>
                No patents registered yet. Patents can be added via the API.
              </p>
            )}
          </>
        )}
      </SectionCard>

      {/* ══════════════════════════════════════════════════════
          SECTION 5 — ANALYTICS
          ══════════════════════════════════════════════════════ */}
      <SectionCard title="Analytics">
        {loading ? <LoadingDots /> : (
          <div className="insight-row">
            {/* Grants by research area */}
            {!errors.stats && stats?.research_areas?.length > 0 && (
              <div className="insight-panel">
                <p className="insight-panel__label">Open Grants by Research Area</p>
                <div className="area-chart">
                  {stats.research_areas.map(({ area, count }) => (
                    <div key={area} className="area-bar-row">
                      <span className="area-bar-label">{area}</span>
                      <div className="area-bar-track">
                        <div className="area-bar-fill" style={{ width: `${(count / maxArea) * 100}%` }} />
                      </div>
                      <span className="area-bar-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Publications by year */}
            {!errors.pubs && pubs?.by_year?.length > 0 && (
              <div className="insight-panel">
                <p className="insight-panel__label">Publications by Year</p>
                <div className="area-chart">
                  {pubs.by_year.map(({ year, count }) => (
                    <div key={year} className="area-bar-row">
                      <span className="area-bar-label">{year}</span>
                      <div className="area-bar-track">
                        <div className="area-bar-fill area-bar-fill--pub"
                          style={{ width: `${(count / maxPubYear) * 100}%` }} />
                      </div>
                      <span className="area-bar-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top journals */}
            {!errors.pubs && pubs?.top_journals?.length > 0 && (
              <div className="insight-panel">
                <p className="insight-panel__label">Top Journals</p>
                <div className="desig-list">
                  {pubs.top_journals.map(({ journal, count }) => (
                    <div key={journal} className="desig-row">
                      <span className="desig-name">{journal}</span>
                      <span className="desig-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Country distribution */}
            {!errors.stats && stats?.countries?.length > 0 && (
              <div className="insight-panel">
                <p className="insight-panel__label">Grants by Country</p>
                <div className="country-chips">
                  {stats.countries.map(({ country, count }) => (
                    <span key={country} className="country-chip">
                      {country} <strong>{count}</strong>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {errors.stats && errors.pubs && (
              <ErrorBanner msg="Could not load analytics data." />
            )}
          </div>
        )}
      </SectionCard>

      {/* ══════════════════════════════════════════════════════
          SECTION 6 — NOTIFICATIONS & ALERTS
          ══════════════════════════════════════════════════════ */}
      <SectionCard
        title="Notifications & Alerts"
        badge={unreadCount > 0 ? unreadCount : null}
        action={
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {alerts && alerts.expiring_soon.length > 0 && unreadCount > 0 && (
              <button className="btn btn--ghost btn--sm" onClick={markAllRead}>
                Mark all read
              </button>
            )}
            <button
              className="btn btn--ghost btn--sm"
              onClick={() => alertsRef.current?.scrollIntoView({ behavior: 'smooth' })}
            >
              View all
            </button>
          </div>
        }
      >
        <div ref={alertsRef}>
          {loading ? <LoadingDots /> : errors.alerts ? <ErrorBanner msg={errors.alerts} /> : (
            <>
              {alerts.expiring_soon.length === 0 ? (
                <div className="alert-empty">
                  <svg viewBox="0 0 20 20" aria-hidden="true" width="20" height="20">
                    <path d="M10 2a8 8 0 1 0 0 16A8 8 0 0 0 10 2zm.75 4.5v4l2.5 1.5-.75 1.3-3.25-2V6.5z"
                      fill="var(--text)" opacity=".4" />
                  </svg>
                  <span>No grants expiring in the next 30 days.</span>
                </div>
              ) : (
                <div className="alerts-list">
                  {alerts.expiring_soon.map(a => {
                    const isRead = readIds.has(a.grant_id)
                    return (
                      <div
                        key={a.grant_id}
                        className={[
                          'alert-item',
                          a.days_left <= 7 ? 'alert-item--urgent' : 'alert-item--warning',
                          isRead ? 'alert-item--read' : '',
                        ].filter(Boolean).join(' ')}
                      >
                        <div className="alert-item__icon" aria-hidden="true">
                          {a.days_left <= 7 ? '🔴' : '🟡'}
                        </div>
                        <div className="alert-item__body">
                          <p className="alert-item__title">
                            {!isRead && <span className="alert-unread-dot" aria-label="unread" />}
                            {a.grant_name}
                          </p>
                          <p className="alert-item__meta">
                            {a.organization}
                            {a.funding_amount && ` · ${fmt(a.funding_amount)}`}
                          </p>
                        </div>
                        <div className="alert-item__right">
                          <span className={`deadline-badge ${a.days_left <= 7 ? 'deadline-badge--urgent' : 'deadline-badge--soon'}`}>
                            {daysLabel(a.days_left)}
                          </span>
                          <div className="alert-item__actions">
                            {a.application_url && (
                              <a href={a.application_url} target="_blank" rel="noopener noreferrer"
                                className="btn btn--ghost btn--sm">
                                Apply
                              </a>
                            )}
                            {!isRead && (
                              <button
                                className="btn btn--ghost btn--sm"
                                onClick={() => markRead(a.grant_id)}
                              >
                                Mark read
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              <div className="alert-info-row">
                <svg viewBox="0 0 16 16" aria-hidden="true" width="14" height="14">
                  <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4h1.5v4.5h-1.5zm0 5.5h1.5V12h-1.5z"
                    fill="currentColor" opacity=".5" />
                </svg>
                Alerts are computed from open grant deadlines. Notification API integration
                can be added when the notifications module is available.
              </div>
            </>
          )}
        </div>
      </SectionCard>
    </div>
  )
}
