import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRightIcon, CubeIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { getProducts } from '../services/api';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import PageHeader from '../components/PageHeader';
import RatingStars from '../components/RatingStars';
import SearchBar from '../components/SearchBar';
import { SkeletonCard } from '../components/LoadingSpinner';
import { formatNumber } from '../utils/helpers';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [search, setSearch] = useState('');
  const loadProducts = useCallback(async (term = '') => { setLoading(true); setFailed(false); try { const response = await getProducts(term, 1000); setProducts(response.products || []); } catch { setFailed(true); toast.error('Products could not be loaded.'); } finally { setLoading(false); } }, []);
  useEffect(() => { loadProducts(''); }, [loadProducts]);
  const handleSearch = (term) => { setSearch(term); loadProducts(term); };

  return <main className="page"><PageHeader title="Products" description="Find a product, then open focused customer feedback and intelligence." /><section className="surface surface-padded"><div className="section-heading"><div><h2>Product catalog</h2><p>Search across products with customer review coverage.</p></div><span className="text-sm text-slate-500">{products.length.toLocaleString()} shown</span></div><div className="max-w-xl"><SearchBar value={search} onSearch={handleSearch} placeholder="Search products…" /></div><div className="mt-5">{loading && <div className="grid gap-3 md:grid-cols-2"><SkeletonCard count={6} /></div>}{failed && <ErrorState title="Products could not be loaded" description="Please try again in a moment." onRetry={() => loadProducts(search)} />}{!loading && !failed && (products.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Product</th><th>Review count</th><th>Average rating</th><th aria-label="Actions" /></tr></thead><tbody>{products.map((product) => <tr key={product.product_name}><td className="product-cell">{product.product_name}</td><td>{formatNumber(product.review_count)}</td><td><RatingStars rating={product.avg_rating} /></td><td><Link className="button-quiet" to={`/products/${encodeURIComponent(product.product_name)}`}>View insights<ArrowRightIcon className="h-3.5 w-3.5" /></Link></td></tr>)}</tbody></table></div> : <EmptyState icon={CubeIcon} title="No products found" description="Try a broader product search." />)}</div></section></main>;
}
