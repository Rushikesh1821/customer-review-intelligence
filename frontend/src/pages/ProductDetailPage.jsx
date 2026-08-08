import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeftIcon, ChatBubbleBottomCenterTextIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import toast from 'react-hot-toast';
import { askAI, exploreReviews, getProductDetails } from '../services/api';
import ChartCard from '../components/ChartCard';
import ErrorState from '../components/ErrorState';
import KpiCard from '../components/KpiCard';
import PageHeader from '../components/PageHeader';
import RatingStars from '../components/RatingStars';
import ReviewCard from '../components/ReviewCard';
import Tabs from '../components/Tabs';
import { LoadingPage, LoadingSpinner } from '../components/LoadingSpinner';
import { formatNumber, formatPercent, formatRating, formatRatingDistribution, formatSentimentDistribution } from '../utils/helpers';

const tabs = [{ id: 'overview', label: 'Overview' }, { id: 'reviews', label: 'Reviews' }, { id: 'complaints', label: 'Complaints' }, { id: 'ai', label: 'AI Insights' }];
const axis = { fill: '#64748b', fontSize: 11 };
function decodeProduct(value) { try { return decodeURIComponent(value || ''); } catch { return value || ''; } }

export default function ProductDetailPage() {
  const { productId } = useParams();
  const productName = useMemo(() => decodeProduct(productId), [productId]);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [tab, setTab] = useState('overview');
  const [reviews, setReviews] = useState(null);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);
  const load = useCallback(async () => { setLoading(true); setFailed(false); try { setDetail(await getProductDetails(productName)); } catch { setFailed(true); toast.error('Product insights could not be loaded.'); } finally { setLoading(false); } }, [productName]);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { setTab('overview'); setReviews(null); setAnswer(null); }, [productName]);
  useEffect(() => { if (tab !== 'reviews' || reviews) return; setReviewsLoading(true); exploreReviews({ page: 1, pageSize: 20, product: productName }).then((response) => setReviews(response.reviews || [])).catch(() => toast.error('Product reviews could not be loaded.')).finally(() => setReviewsLoading(false)); }, [tab, reviews, productName]);
  const submitQuestion = async (event) => { event.preventDefault(); if (!question.trim()) return toast.error('Enter a question about this product.'); setAsking(true); try { setAnswer(await askAI(question.trim(), productName, 6)); } catch { toast.error('The AI assistant could not answer that question.'); } finally { setAsking(false); } };
  if (loading) return <main className="page"><LoadingPage message="Building product intelligence…" /></main>;
  if (failed || !detail) return <main className="page"><ErrorState title="Product insights could not be loaded" description="Please try again in a moment." onRetry={load} /></main>;
  const breakdown = detail.sentiment_breakdown || {};
  const sentimentData = formatSentimentDistribution({ Positive: breakdown.Positive, Neutral: breakdown.Neutral, Negative: breakdown.Negative });
  const ratingData = formatRatingDistribution(detail.rating_distribution);

  return <main className="page"><PageHeader title={detail.product_name} description="Customer feedback, ratings, and AI-assisted product intelligence." actions={<Link className="button-secondary" to="/products"><ArrowLeftIcon className="h-4 w-4" />All products</Link>} /><section className="surface surface-padded"><div className="flex flex-wrap items-center gap-5"><RatingStars rating={detail.average_rating} /><span className="text-sm text-slate-500">{formatNumber(detail.total_reviews)} reviews</span><span className="sentiment-badge sentiment-positive">{formatPercent(breakdown.positive_pct)} positive</span></div><div className="mt-6"><Tabs tabs={tabs} activeTab={tab} onChange={setTab} /></div></section>{tab === 'overview' && <section className="mt-5"><div className="kpi-grid"><KpiCard label="Average rating" value={`${formatRating(detail.average_rating)} / 5`} detail="Customer-assigned rating" /><KpiCard label="Review count" value={formatNumber(detail.total_reviews)} detail="Available customer feedback" /><KpiCard label="Positive sentiment" value={formatPercent(breakdown.positive_pct)} detail={`${formatNumber(breakdown.Positive)} positive reviews`} tone="positive" /><KpiCard label="Negative sentiment" value={formatPercent(breakdown.negative_pct)} detail={`${formatNumber(breakdown.Negative)} reviews requiring attention`} tone="negative" /></div><div className="grid-two mt-5"><ChartCard title="Sentiment distribution" description="How customers feel about this product."><div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={sentimentData} dataKey="value" innerRadius={55} outerRadius={85} paddingAngle={3} stroke="none">{sentimentData.map((item) => <Cell key={item.name} fill={item.fill} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div></ChartCard><ChartCard title="Rating distribution" description="Customer ratings from one to five stars."><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={ratingData} margin={{ top: 8, right: 5, bottom: 0, left: -18 }}><XAxis dataKey="star" tick={axis} axisLine={false} tickLine={false} /><YAxis tick={axis} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="count" fill="#6366f1" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div></ChartCard></div></section>}{tab === 'reviews' && <section className="surface surface-padded mt-5"><div className="section-heading"><div><h2>Product reviews</h2><p>Customer feedback for this product.</p></div></div>{reviewsLoading ? <LoadingPage message="Loading product reviews…" /> : <div className="review-list">{reviews?.map((review, index) => <ReviewCard key={review.id || index} review={review} showProduct={false} />)}</div>}</section>}{tab === 'complaints' && <section className="mt-5"><div className="surface surface-padded"><div className="section-heading"><div><h2>Customer complaints</h2><p>Negative feedback and low-rating review examples.</p></div></div>{detail.top_complaints?.length ? <div className="review-list">{detail.top_complaints.map((review) => <ReviewCard key={review.id} review={{ ...review, product: detail.product_name, sentiment: 'Negative' }} showProduct={false} />)}</div> : <p className="text-sm text-slate-500">No complaint examples are available for this product.</p>}</div></section>}{tab === 'ai' && <section className="mt-5"><div className="ai-panel"><div className="ai-panel-head"><h2><SparklesIcon className="h-4 w-4" />AI insights</h2><span className="text-xs font-semibold text-indigo-600">Product-specific</span></div><div className="ai-panel-body">{detail.ai_summary || 'No AI summary is available for this product.'}</div></div><form className="surface surface-padded mt-5" onSubmit={submitQuestion}><div className="section-heading"><div><h2>Ask AI about this product</h2><p>Retrieval is automatically restricted to this product.</p></div></div><div className="flex flex-col gap-3 sm:flex-row"><input className="input flex-1" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What do customers say about quality?" /><button type="submit" className="button-primary" disabled={asking}>{asking ? <><LoadingSpinner size="sm" />Analyzing…</> : <><ChatBubbleBottomCenterTextIcon className="h-4 w-4" />Ask AI</>}</button></div></form>{answer && <div className="ai-panel mt-5"><div className="ai-panel-head"><h2><SparklesIcon className="h-4 w-4" />AI generated answer</h2><span className="text-xs font-semibold text-indigo-600">Based on {answer.review_count} reviews</span></div><div className="ai-panel-body">{answer.answer}</div></div>}</section>}</main>;
}
