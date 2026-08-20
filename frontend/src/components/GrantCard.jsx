export default function GrantCard({ grant, rank }) {
  const score = grant.match_score ?? 0
  const scoreColor =
    score >= 70 ? 'var(--score-high)' :
    score >= 40 ? 'var(--score-mid)' :
    'var(--score-low)'

  const formattedAmount = grant.funding_amount
    ? `$${Number(grant.funding_amount).toLocaleString()}`
    : 'Not specified'

  const formattedDeadline = grant.deadline
    ? new Date(grant.deadline).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
      })
    : 'No deadline listed'

  return (
    <article className="grant-card">
      <div className="grant-card__header">
        <span className="grant-card__rank">#{rank}</span>
        <div
          className="grant-card__score"
          style={{ '--score-color': scoreColor }}
          title={`Match score: ${score}/100`}
        >
          <svg viewBox="0 0 36 36" className="score-ring" aria-hidden="true">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--border)" strokeWidth="3" />
            <circle
              cx="18" cy="18" r="15.9" fill="none"
              stroke={scoreColor} strokeWidth="3"
              strokeDasharray={`${score} 100`}
              strokeLinecap="round"
              transform="rotate(-90 18 18)"
            />
          </svg>
          <span className="score-value">{score}</span>
        </div>
      </div>

      <div className="grant-card__body">
        <h3 className="grant-card__title">{grant.grant_name}</h3>
        <p className="grant-card__org">{grant.organization}</p>

        <div className="grant-card__meta">
          <span className="meta-item">
            <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm0 1.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zM7.25 5v3.5l3 1.75.5-.87-2.5-1.44V5z" fill="currentColor"/></svg>
            {formattedDeadline}
          </span>
          <span className="meta-item">
            <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm.75 3.5v1.25h1.5v1.5h-1.5v4.25h-1.5V7.25H5.75v-1.5h1.5V4.5z" fill="currentColor"/></svg>
            {formattedAmount}
          </span>
        </div>

        {grant.matching_reasons?.length > 0 && (
          <ul className="grant-card__reasons">
            {grant.matching_reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="grant-card__footer">
        {grant.application_url ? (
          <a
            href={grant.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn--primary"
          >
            Apply Now
          </a>
        ) : (
          <span className="btn btn--disabled">No URL available</span>
        )}
      </div>
    </article>
  )
}
