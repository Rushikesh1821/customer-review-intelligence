import { useEffect, useState } from 'react';
import { ArrowsRightLeftIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import toast from 'react-hot-toast';
import { compareProducts, getAnalytics, getProducts } from '../services/api';
import { useApi } from '../hooks/useApi';
import ChartCard from '../components/ChartCard';
import ErrorState from '../components/ErrorState';
import PageHeader from '../components/PageHeader';
import RatingStars from '../components/RatingStars';
import Tabs from '../components/Tabs';
import { LoadingPage, LoadingSpinner } from '../components/LoadingSpinner';
import { formatNumber, formatRatingDistribution, formatSentimentDistribution } from '../utils/helpers';

const tabs = [{ id: 'overview', label: 'Overview' }, { id: 'sentiment', label: 'Sentiment' }, { id: 'ratings', label: 'Ratings' }, { id: 'products', label: 'Products' }];
const axis = { fill: '#64748b', fontSize: 11 };

export default function AnalyticsPage() {
  const { data, loading, execute } = useApi(getAnalytics);
  const [tab, setTab] = useState('overview');
  const [products, setProducts] = useState([]);
  const [productA, setProductA] = useState('');
  const [productB, setProductB] = useState('');
  const [comparison, setComparison] = useState(null);
  const [comparing, setComparing] = useState(false);
  useEffect(() => { execute().catch(() => undefined); getProducts('', 1000).then((response) => setProducts(response.products || [])).catch(() => undefined); }, [execute]);
  const compare = async (event) => { event.preventDefault(); if (!productA || !productB || productA === productB) return toast.error('Choose two different products to compare.'); setComparing(true); setComparison(null); try { setComparison(await compareProducts(productA, productB)); } catch { toast.error('The product comparison could not be generated.'); } finally { setComparing(false); } };
  if (loading && !data) return <main className="page"><LoadingPage message="Loading analytics…" /></main>;
  if (!data) return <main className="page"><ErrorState title="Analytics could not be loaded" description="Please try again in a moment." onRetry={() => execute().catch(() => undefined)} /></main>;
  const sentiment = formatSentimentDistribution(data.sentiment_distribution);
  const ratings = formatRatingDistribution(data.rating_distribution);
  const productsChart = data.top_products?.slice(0, 8).map((item) => ({ ...item, shortName: item.product_name.length > 24 ? `${item.product_name.slice(0, 24)}…` : item.product_name })).reverse();

  return <main className="page"><PageHeader title="Analytics" description="Go deeper into customer sentiment, ratings, and product-level feedback patterns." /><section className="surface surface-padded"><Tabs tabs={tabs} activeTab={tab} onChange={setTab} /></section>{tab === 'overview' && <section className="grid-two mt-5"><SentimentChart data={sentiment} /><RatingChart data={ratings} /></section>}{tab === 'sentiment' && <section className="mt-5"><SentimentChart data={sentiment} full /></section>}{tab === 'ratings' && <section className="mt-5"><RatingChart data={ratings} full /></section>}{tab === 'products' && <section className="mt-5"><ChartCard title="Most reviewed products" description="Products with the highest customer feedback volume."><div className="h-[380px]"><ResponsiveContainer width="100%" height="100%"><BarChart data={productsChart} layout="vertical" margin={{ top: 0, right: 18, bottom: 0, left: 0 }}><XAxis type="number" tick={axis} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="shortName" width={180} tick={axis} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => [formatNumber(value), 'Reviews']} /><Bar dataKey="review_count" fill="#6366f1" radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer></div></ChartCard></section>}<section className="surface surface-padded mt-5"><div className="section-heading"><div><h2 className="flex items-center gap-2"><ArrowsRightLeftIcon className="h-4 w-4 text-indigo-600" />Product comparison</h2><p>Compare two products using customer review evidence.</p></div></div><form className="grid gap-3 md:grid-cols-[1fr_1fr_auto]" onSubmit={compare}><select className="select" value={productA} onChange={(event) => setProductA(event.target.value)}><option value="">Choose first product</option>{products.map((product) => <option key={product.product_name} value={product.product_name}>{product.product_name}</option>)}</select><select className="select" value={productB} onChange={(event) => setProductB(event.target.value)}><option value="">Choose second product</option>{products.map((product) => <option key={product.product_name} value={product.product_name}>{product.product_name}</option>)}</select><button type="submit" className="button-primary" disabled={comparing}>{comparing ? <><LoadingSpinner size="sm" />Comparing…</> : 'Compare products'}</button></form>{comparison && <div className="grid-two mt-5"><div className="grid gap-3"><ComparisonCard product={comparison.product_a} /><ComparisonCard product={comparison.product_b} /></div><div className="ai-panel"><div className="ai-panel-head"><h2><SparklesIcon className="h-4 w-4" />AI comparison</h2><span className="text-xs font-semibold text-indigo-600">Review-grounded</span></div><div className="ai-panel-body">{comparison.ai_comparison}</div></div></div>}</section></main>;
}

function SentimentChart({ data, full = false }) { return <ChartCard title="Sentiment distribution" description="Customer feedback classified by the sentiment model."><div className={full ? 'flex h-[360px] items-center justify-center' : 'h-64'}><ResponsiveContainer width={full ? '60%' : '100%'} height="100%"><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={full ? 92 : 55} outerRadius={full ? 135 : 86} paddingAngle={3} stroke="none">{data.map((item) => <Cell key={item.name} fill={item.fill} />)}</Pie><Tooltip formatter={(value) => [formatNumber(value), 'Reviews']} /></PieChart></ResponsiveContainer></div></ChartCard>; }
function RatingChart({ data, full = false }) { return <ChartCard title="Rating distribution" description="Star ratings customers have assigned to products."><div className={full ? 'h-[360px]' : 'h-64'}><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}><XAxis dataKey="star" tick={axis} axisLine={false} tickLine={false} /><YAxis tick={axis} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => [formatNumber(value), 'Reviews']} /><Bar dataKey="count" fill="#6366f1" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div></ChartCard>; }
function ComparisonCard({ product }) { if (!product || product.error) return <div className="surface surface-padded text-sm text-red-700">{product?.error || 'Product information is unavailable.'}</div>; return <div className="surface surface-padded"><h3 className="truncate text-sm font-bold text-slate-900" title={product.product_name}>{product.product_name}</h3><div className="mt-3 flex items-center justify-between"><RatingStars rating={product.average_rating} /><span className="text-sm text-slate-500">{formatNumber(product.total_reviews)} reviews</span></div></div>; }
