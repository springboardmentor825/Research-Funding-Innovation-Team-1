export default function StatCard({ label, value, sub, accent, onClick }) {
  const classes = [
    'stat-card',
    accent ? 'stat-card--accent' : '',
    onClick ? 'stat-card--clickable' : '',
  ].filter(Boolean).join(' ')

  const inner = (
    <>
      <span className="stat-card__value">{value ?? '—'}</span>
      <span className="stat-card__label">{label}</span>
      {sub && <span className="stat-card__sub">{sub}</span>}
    </>
  )

  if (onClick) {
    return (
      <button className={classes} onClick={onClick} type="button">
        {inner}
      </button>
    )
  }

  return <div className={classes}>{inner}</div>
}
