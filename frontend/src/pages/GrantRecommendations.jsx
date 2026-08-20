import { useState } from 'react'
import { matchGrants } from '../services/grants'
import GrantCard from '../components/GrantCard'

const INITIAL_FORM = {
  research_area: '',
  keywords: '',
  country: '',
  eligibility: '',
}

export default function GrantRecommendations() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [results, setResults] = useState(null)   // null = not searched yet
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResults(null)

    const keywords = form.keywords
      .split(',')
      .map((k) => k.trim())
      .filter(Boolean)

    if (!form.research_area.trim()) {
      setError('Research area is required.')
      return
    }
    if (keywords.length === 0) {
      setError('Please enter at least one keyword.')
      return
    }

    setLoading(true)
    try {
      const payload = {
        research_area: form.research_area.trim(),
        keywords,
        ...(form.country.trim() && { country: form.country.trim() }),
        ...(form.eligibility.trim() && { eligibility: form.eligibility.trim() }),
      }
      const data = await matchGrants(payload)
      setResults(data.matches ?? [])
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setForm(INITIAL_FORM)
    setResults(null)
    setError(null)
  }

  return (
    <div className="page">
      <header className="page__header">
        <h1>Grant Recommendations</h1>
        <p className="page__subtitle">
          Enter your research profile to discover funding opportunities ranked by relevance.
        </p>
      </header>

      <section className="search-section">
        <form className="search-form" onSubmit={handleSubmit} noValidate>
          <div className="form-grid">
            <div className="form-field form-field--full">
              <label htmlFor="research_area">
                Research Area <span className="required">*</span>
              </label>
              <input
                id="research_area"
                name="research_area"
                type="text"
                placeholder="e.g. Artificial Intelligence"
                value={form.research_area}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field form-field--full">
              <label htmlFor="keywords">
                Keywords <span className="required">*</span>
                <span className="field-hint"> — comma-separated</span>
              </label>
              <input
                id="keywords"
                name="keywords"
                type="text"
                placeholder="e.g. machine learning, deep learning, computer vision"
                value={form.keywords}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="country">Country</label>
              <input
                id="country"
                name="country"
                type="text"
                placeholder="e.g. India"
                value={form.country}
                onChange={handleChange}
              />
            </div>

            <div className="form-field">
              <label htmlFor="eligibility">Eligibility</label>
              <input
                id="eligibility"
                name="eligibility"
                type="text"
                placeholder="e.g. University Researcher"
                value={form.eligibility}
                onChange={handleChange}
              />
            </div>
          </div>

          {error && (
            <div className="alert alert--error" role="alert">
              <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4h1.5v4.5h-1.5zm0 5.5h1.5V12h-1.5z" fill="currentColor"/></svg>
              {error}
            </div>
          )}

          <div className="form-actions">
            <button type="submit" className="btn btn--primary btn--lg" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" aria-hidden="true" />
                  Searching…
                </>
              ) : (
                'Find Matching Grants'
              )}
            </button>
            {results !== null && (
              <button type="button" className="btn btn--ghost" onClick={handleReset}>
                Clear
              </button>
            )}
          </div>
        </form>
      </section>

      {loading && (
        <div className="loading-state" aria-live="polite">
          <div className="loading-dots">
            <span /><span /><span />
          </div>
          <p>Matching your profile against available grants…</p>
        </div>
      )}

      {!loading && results !== null && (
        <section className="results-section" aria-live="polite">
          <div className="results-header">
            <h2>
              {results.length === 0
                ? 'No matching grants found'
                : `${results.length} Funding ${results.length === 1 ? 'Opportunity' : 'Opportunities'} Found`}
            </h2>
            {results.length > 0 && (
              <p className="results-subtitle">Sorted by match score — highest first</p>
            )}
          </div>

          {results.length === 0 ? (
            <div className="empty-state">
              <svg viewBox="0 0 48 48" aria-hidden="true" className="empty-icon">
                <circle cx="24" cy="24" r="22" fill="none" stroke="var(--border)" strokeWidth="2"/>
                <path d="M16 24h16M24 16v16" stroke="var(--border)" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <p>No matching funding opportunities found for your profile.</p>
              <p className="empty-hint">Try broadening your research area or adding more keywords.</p>
            </div>
          ) : (
            <div className="results-grid">
              {results.map((grant, i) => (
                <GrantCard key={grant.grant_id} grant={grant} rank={i + 1} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
