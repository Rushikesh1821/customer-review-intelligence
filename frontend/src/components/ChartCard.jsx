export default function ChartCard({ title, description, action, children, className = '' }) {
  return (
    <section className={`surface surface-padded ${className}`}>
      <div className="section-heading"><div><h2>{title}</h2>{description && <p>{description}</p>}</div>{action}</div>
      {children}
    </section>
  );
}
