export default function SentimentBadge({ sentiment = 'Neutral' }) {
  const normalized = String(sentiment).toLowerCase();
  const className = normalized === 'positive' ? 'sentiment-positive' : normalized === 'negative' ? 'sentiment-negative' : 'sentiment-neutral';
  return <span className={`sentiment-badge ${className}`}>{sentiment}</span>;
}
