import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function ErrorState({ title = 'Something went wrong', description = 'Please try again in a moment.', onRetry }) {
  return <div className="error-state"><div className="empty-state-icon"><ExclamationTriangleIcon className="h-5 w-5" /></div><h3>{title}</h3><p>{description}</p>{onRetry && <button type="button" className="button-secondary mt-4" onClick={onRetry}>Try again</button>}</div>;
}
