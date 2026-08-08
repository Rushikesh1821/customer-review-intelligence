import { useState } from 'react';
import RatingStars from './RatingStars';
import SentimentBadge from './SentimentBadge';

const previewLength = 240;

export default function ReviewCard({ review, showProduct = true }) {
  const [expanded, setExpanded] = useState(false);
  const text = String(review.text || 'No review text provided.');
  const needsExpansion = text.length > previewLength;
  const visibleText = expanded || !needsExpansion ? text : `${text.slice(0, previewLength).trimEnd()}…`;

  return (
    <article className="review-card">
      <div className="review-card-head">
        <div className="min-w-0">{showProduct && <p className="review-product" title={review.product}>{review.product || 'Unknown product'}</p>}<div className="review-meta"><RatingStars rating={review.rating} /><SentimentBadge sentiment={review.sentiment} /></div></div>
        {review.similarity_score !== undefined && <span className="text-xs font-semibold text-indigo-600">{Math.round(review.similarity_score * 100)}% match</span>}
      </div>
      <p className="review-text">{visibleText}</p>
      <div className="review-card-foot"><span className="review-length">{text.length.toLocaleString()} characters</span>{needsExpansion && <button type="button" className="link-button" onClick={() => setExpanded((value) => !value)}>{expanded ? 'Show less' : 'Read more'}</button>}</div>
    </article>
  );
}
