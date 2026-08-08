import { useCallback, useEffect, useState } from 'react';
import { AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { exploreReviews, getProducts } from '../services/api';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import PageHeader from '../components/PageHeader';
import Pagination from '../components/Pagination';
import ReviewCard from '../components/ReviewCard';
import SearchBar from '../components/SearchBar';
import { SkeletonCard } from '../components/LoadingSpinner';

const initialFilters = { product: '', sentiment: '', rating: '', isSemantic: false };

export default function ReviewsPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [products, setProducts] = useState([]);
  const loadReviews = useCallback(async () => { setLoading(true); setFailed(false); try { setData(await exploreReviews({ page, pageSize: 20, search, ...filters })); } catch { setFailed(true); toast.error('Reviews could not be loaded.'); } finally { setLoading(false); } }, [filters, page, search]);
  useEffect(() => { loadReviews(); }, [loadReviews]);
  useEffect(() => { getProducts('', 1000).then((response) => setProducts(response.products || [])).catch(() => undefined); }, []);
  const setFilter = (name, value) => { setPage(1); setFilters((current) => ({ ...current, [name]: value })); };
  const clear = () => { setPage(1); setSearch(''); setFilters(initialFilters); };

  return <main className="page"><PageHeader title="Customer Reviews" description="Explore and filter customer feedback across the complete review corpus." /><section className="filter-bar"><SearchBar value={search} onSearch={(value) => { setPage(1); setSearch(value); }} placeholder={filters.isSemantic ? 'Describe feedback to find…' : 'Search reviews or products…'} /><label><span className="field-label">Product</span><select className="select" value={filters.product} onChange={(event) => setFilter('product', event.target.value)}><option value="">All products</option>{products.map((item) => <option key={item.product_name} value={item.product_name}>{item.product_name}</option>)}</select></label><label><span className="field-label">Sentiment</span><select className="select" value={filters.sentiment} onChange={(event) => setFilter('sentiment', event.target.value)}><option value="">All sentiment</option><option>Positive</option><option>Neutral</option><option>Negative</option></select></label><label><span className="field-label">Rating</span><select className="select" value={filters.rating} onChange={(event) => setFilter('rating', event.target.value)}><option value="">All ratings</option>{[5, 4, 3, 2, 1].map((rating) => <option key={rating} value={rating}>{rating} stars</option>)}</select></label><button type="button" className="button-secondary" onClick={clear}>Clear filters</button></section><div className="mt-3 flex items-center justify-between gap-4"><label className="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-600"><input type="checkbox" checked={filters.isSemantic} onChange={(event) => setFilter('isSemantic', event.target.checked)} className="h-4 w-4 rounded border-slate-300 text-indigo-600" /><AdjustmentsHorizontalIcon className="h-4 w-4 text-indigo-600" />Use semantic search</label>{data && <span className="text-sm text-slate-500"><strong className="text-slate-900">{data.total?.toLocaleString()}</strong> matching reviews</span>}</div><section className="mt-5">{loading && !data && <div className="review-list"><SkeletonCard count={5} /></div>}{failed && <ErrorState title="Reviews could not be loaded" description="Please try again in a moment." onRetry={loadReviews} />}{data && !loading && !failed && (data.reviews?.length ? <><div className="review-list">{data.reviews.map((review, index) => <ReviewCard key={review.id || index} review={review} />)}</div><Pagination page={data.page || 1} totalPages={data.total_pages || 1} onPageChange={setPage} /></> : <EmptyState title="No reviews found" description="Try changing your search or filters." action={{ label: 'Clear filters', onClick: clear }} />)}</section></main>;
}
