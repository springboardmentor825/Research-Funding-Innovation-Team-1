export default function GrantsTable({ grants }) {
  if (!grants.length) {
    return (
      <div className="empty-state">
        <p>No funding opportunities available.</p>
      </div>
    )
  }

  return (
    <div className="grants-table-wrap">
      <table className="grants-table">
        <thead>
          <tr>
            <th>Grant Name</th>
            <th>Organization</th>
            <th>Research Area</th>
            <th>Funding Amount</th>
            <th>Deadline</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {grants.map((g) => (
            <tr key={g.id}>
              <td className="grants-table__name">{g.grant_name}</td>
              <td>{g.funding_organization}</td>
              <td>
                {g.research_area
                  ? <span className="tag">{g.research_area}</span>
                  : <span className="muted">—</span>}
              </td>
              <td>
                {g.funding_amount
                  ? `$${Number(g.funding_amount).toLocaleString()}`
                  : <span className="muted">—</span>}
              </td>
              <td>
                {g.deadline
                  ? new Date(g.deadline).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                  : <span className="muted">—</span>}
              </td>
              <td>
                <span className={`status-badge status-badge--${g.status ?? 'open'}`}>
                  {g.status ?? 'open'}
                </span>
              </td>
              <td>
                {g.application_url && (
                  <a href={g.application_url} target="_blank" rel="noopener noreferrer" className="btn btn--ghost btn--sm">
                    Apply
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
