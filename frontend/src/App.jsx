import { useEffect, useState } from 'react'
import Dashboard from './pages/Dashboard'
import GrantRecommendations from './pages/GrantRecommendations'
import ResearchDashboard from './pages/ResearchDashboard'
import './App.css'

const PAGES = {
  dashboard: 'dashboard',
  recommendations: 'recommendations',
  research: 'research',
}

/* Bell SVG — inline so no extra dependency */
function BellIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true" className="bell-icon">
      <path
        d="M10 2a6 6 0 0 0-6 6v2.586l-1.707 1.707A1 1 0 0 0 3 14h14a1 1 0 0 0 .707-1.707L16 10.586V8a6 6 0 0 0-6-6z"
        stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"
      />
      <path d="M8 14a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

/* Hamburger SVG */
function HamburgerIcon({ open }) {
  return open ? (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true" className="hamburger-icon">
      <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ) : (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true" className="hamburger-icon">
      <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

export default function App() {
  const [page, setPage] = useState(PAGES.dashboard)
  const [alertCount, setAlertCount] = useState(0)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  /* Fetch alert count once on mount so the bell badge is always visible */
  useEffect(() => {
    fetch('/api/insights/alerts')
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setAlertCount(data.expiring_count ?? 0) })
      .catch(() => {})
  }, [])

  function navigate(p) {
    setPage(p)
    setMobileNavOpen(false)
  }

  const navItems = [
    { key: PAGES.dashboard,       label: 'Dashboard' },
    { key: PAGES.research,        label: 'Research Dashboard' },
    { key: PAGES.recommendations, label: 'Grant Recommendations' },
  ]

  return (
    <>
      <nav className="navbar">
        <div className="navbar__brand">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="navbar__logo">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="var(--accent)" strokeWidth="2" fill="none"
              strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Research Funding Intelligence
        </div>

        {/* Desktop nav links */}
        <ul className="navbar__links">
          {navItems.map(({ key, label }) => (
            <li key={key}>
              <button
                className={`navbar__link navbar__btn${page === key ? ' navbar__link--active' : ''}`}
                onClick={() => navigate(key)}
              >
                {label}
              </button>
            </li>
          ))}
        </ul>

        {/* Right-side controls */}
        <div className="navbar__controls">
          {/* Notification bell — navigates to Research Dashboard alerts section */}
          <button
            className={`bell-btn${page === PAGES.research ? ' bell-btn--active' : ''}`}
            onClick={() => navigate(PAGES.research)}
            aria-label={`Notifications${alertCount > 0 ? ` — ${alertCount} active` : ''}`}
            title="View alerts"
          >
            <BellIcon />
            {alertCount > 0 && (
              <span className="bell-badge" aria-hidden="true">{alertCount > 9 ? '9+' : alertCount}</span>
            )}
          </button>

          {/* Mobile hamburger */}
          <button
            className="hamburger-btn"
            onClick={() => setMobileNavOpen(o => !o)}
            aria-label={mobileNavOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileNavOpen}
          >
            <HamburgerIcon open={mobileNavOpen} />
          </button>
        </div>
      </nav>

      {/* Mobile nav drawer */}
      {mobileNavOpen && (
        <div className="mobile-nav" role="navigation" aria-label="Mobile navigation">
          {navItems.map(({ key, label }) => (
            <button
              key={key}
              className={`mobile-nav__item${page === key ? ' mobile-nav__item--active' : ''}`}
              onClick={() => navigate(key)}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      <main className="main-content">
        {page === PAGES.dashboard && <Dashboard onNavigate={navigate} />}
        {page === PAGES.research && <ResearchDashboard />}
        {page === PAGES.recommendations && <GrantRecommendations />}
      </main>

      <footer className="footer">
        <p>Research Funding &amp; Innovation Intelligence Platform</p>
      </footer>
    </>
  )
}
