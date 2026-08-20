import GrantRecommendations from './pages/GrantRecommendations'
import './App.css'

export default function App() {
  return (
    <>
      <nav className="navbar">
        <div className="navbar__brand">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="navbar__logo">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="var(--accent)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Research Funding Intelligence
        </div>
        <ul className="navbar__links">
          <li><a href="#" className="navbar__link navbar__link--active">Grant Recommendations</a></li>
        </ul>
      </nav>

      <main className="main-content">
        <GrantRecommendations />
      </main>

      <footer className="footer">
        <p>Research Funding &amp; Innovation Intelligence Platform</p>
      </footer>
    </>
  )
}
