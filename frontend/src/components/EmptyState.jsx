import { InboxIcon } from '@heroicons/react/24/outline';

export default function EmptyState({ title = 'No results found', description = 'Try adjusting your filters.', icon: Icon = InboxIcon, action }) {
  return <div className="empty-state"><div className="empty-state-icon"><Icon className="h-5 w-5" /></div><h3>{title}</h3><p>{description}</p>{action && <button type="button" className="button-secondary mt-4" onClick={action.onClick}>{action.label}</button>}</div>;
}
