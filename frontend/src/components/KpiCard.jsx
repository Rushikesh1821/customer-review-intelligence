export default function KpiCard({ label, value, detail, icon: Icon, tone = 'indigo' }) {
  return (
    <article className="kpi-card">
      <div className="kpi-card-top"><span className="kpi-label">{label}</span>{Icon && <span className={`kpi-icon ${tone === 'positive' ? 'positive' : tone === 'negative' ? 'negative' : tone === 'neutral' ? 'neutral' : ''}`}><Icon className="h-4 w-4" /></span>}</div>
      <p className="kpi-value">{value}</p>
      {detail && <p className="kpi-detail">{detail}</p>}
    </article>
  );
}
