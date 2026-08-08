export default function PageHeader({ title, description, actions }) {
  return (
    <div className="page-header">
      <div><h1 className="page-heading">{title}</h1>{description && <p className="page-description">{description}</p>}</div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}
