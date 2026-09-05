export default function SectionCard({ title, badge, children, action }) {
  return (
    <section className="dash-section">
      <div className="dash-section__header">
        <h2 className="dash-section__title">
          {title}
          {badge != null && <span className="section-badge">{badge}</span>}
        </h2>
        {action}
      </div>
      {children}
    </section>
  )
}
