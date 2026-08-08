import { StarIcon } from '@heroicons/react/24/solid';

export default function RatingStars({ rating, showValue = true }) {
  const roundedRating = Math.round(Number(rating) || 0);
  return <span className="rating-stars" aria-label={`${Number(rating || 0).toFixed(1)} out of 5 stars`}>{Array.from({ length: 5 }, (_, index) => <StarIcon key={index} className={index < roundedRating ? '' : 'empty'} />)}{showValue && <span className="rating-number">{Number(rating || 0).toFixed(1)}</span>}</span>;
}
