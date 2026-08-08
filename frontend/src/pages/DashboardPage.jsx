import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChartBarIcon, FaceFrownIcon, FaceSmileIcon, StarIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getDashboard } from '../services/api';
import { useApi } from '../hooks/useApi';
import { formatNumber, formatPercent, formatRating, formatRatingDistribution, formatSentimentDistribution } from '../utils/helpers';
import ChartCard from '../components/ChartCard';
import ErrorState from '../components/ErrorState';
import KpiCard from '../components/KpiCard';
import PageHeader from '../components/PageHeader';
import RatingStars from '../components/RatingStars';
import ReviewCard from '../components/ReviewCard';
import { SkeletonCard, SkeletonStats } from '../components/LoadingSpinner';

const axis = { fill: '#64748b', fontSize: 11 };

function buildInsights(data) {
  const topProduct = data.top_products?.[0];
  return [
    `${formatPercent(data.positive_percentage)} of classified reviews are positive, indicating generally healthy customer sentiment.`,
    `${formatPercent(data.negative_percentage)} of reviews are negative and should be prioritized for issue discovery.`,
    topProduct ? `${topProduct.product_name} currently generates the most feedback, with ${formatNumber(topProduct.review_count)} reviews.` : 'Review data is ready for deeper exploration.',
  ];
}

export default function DashboardPage() {
  const { data, loading, execute } = useApi(getDashboard);
  useEffect(() => { execute().catch(() => undefined); }, [execute]);

  if (loading && !data) return <main className="page"><SkeletonStats /><div className="grid-two mt-5"><SkeletonCard /><SkeletonCard /></div></main>;
  if (!data) return <main className="page"><ErrorState title="Dashboard could not be loaded" description="The platform data is temporarily unavailable. Please try again." onRetry={() => execute().catch(() => undefined)} /></main>;

  const sentimentData = formatSentimentDistribution(data.sentiment_distribution);
  const ratingData = formatRatingDistribution(data.rating_distribution);

  return (
    <main className="page">
      <PageHeader title="Good morning" description="Understand what customers love, dislike, and ask about your products." actions={<button type="button" className="button-secondary" onClick={() => execute().catch(() => undefined)} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh data'}</button>} />
      <section className="kpi-grid" aria-label="Overview metrics">
        <KpiCard label="Total reviews" value={formatNumber(data.total_reviews)} detail="Across the review corpus" icon={ChartBarIcon} />
        <KpiCard label="Average rating" value={`${formatRating(data.average_rating)} / 5`} detail="Customer-assigned ratings" icon={StarIcon} tone="neutral" />
        <KpiCard label="Positive reviews" value={formatPercent(data.positive_percentage)} detail={`${formatNumber(data.sentiment_distribution?.Positive)} positive signals`} icon={FaceSmileIcon} tone="positive" />
        <KpiCard label="Negative reviews" value={formatPercent(data.negative_percentage)} detail={`${formatNumber(data.sentiment_distribution?.Negative)} require attention`} icon={FaceFrownIcon} tone="negative" />
      </section>

      <section className="grid-two mt-5">
        <ChartCard title="Sentiment overview" description="Distribution of model-classified customer sentiment.">
          <div className="flex h-64 flex-col items-center justify-center gap-5 sm:flex-row"><div className="h-44 w-44"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={sentimentData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={72} paddingAngle={3} stroke="none">{sentimentData.map((entry) => <Cell key={entry.name} fill={entry.fill} />)}</Pie><Tooltip formatter={(value) => [formatNumber(value), 'Reviews']} /></PieChart></ResponsiveContainer></div><div className="grid gap-3">{sentimentData.map((item) => <div key={item.name} className="flex min-w-44 items-center justify-between gap-6 text-sm"><span className="flex items-center gap-2 text-slate-600"><span className="h-2.5 w-2.5 rounded-full" style={{ background: item.fill }} />{item.name}</span><strong className="text-slate-900">{formatPercent((item.value / data.total_reviews) * 100)}</strong></div>)}</div></div>
        </ChartCard>
        <ChartCard title="Rating distribution" description="How customers score products across the platform.">
          <div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={ratingData} margin={{ top: 8, right: 4, bottom: 0, left: -18 }}><XAxis dataKey="star" tick={axis} axisLine={false} tickLine={false} /><YAxis tick={axis} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => [formatNumber(value), 'Reviews']} /><Bar dataKey="count" fill="#6366f1" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div>
        </ChartCard>
      </section>

      <section className="grid-main-aside mt-5">
        <div className="surface surface-padded"><div className="section-heading"><div><h2>Top products</h2><p>Products receiving the most customer feedback.</p></div><Link className="button-quiet" to="/products">View catalog</Link></div><div className="table-wrap"><table className="data-table"><thead><tr><th>Product</th><th>Reviews</th><th>Rating</th></tr></thead><tbody>{data.top_products?.slice(0, 5).map((product) => <tr key={product.product_name}><td className="product-cell"><Link className="text-inherit no-underline hover:text-indigo-600" to={`/products/${encodeURIComponent(product.product_name)}`}>{product.product_name}</Link></td><td>{formatNumber(product.review_count)}</td><td><RatingStars rating={product.avg_rating} /></td></tr>)}</tbody></table></div></div>
        <aside className="ai-panel"><div className="ai-panel-head"><h2><SparklesIcon className="h-4 w-4" />Intelligence highlights</h2><span className="text-xs font-semibold text-indigo-600">Live data</span></div><div className="ai-panel-body"><div className="insight-list">{buildInsights(data).map((insight) => <div key={insight} className="insight-row"><SparklesIcon />{insight}</div>)}</div></div></aside>
      </section>

      <section className="surface surface-padded mt-5"><div className="section-heading"><div><h2>Recent customer feedback</h2><p>A small sample of feedback from the review corpus.</p></div><Link className="button-quiet" to="/reviews">View all reviews</Link></div><div className="review-list">{data.recent_reviews?.slice(0, 5).map((review) => <ReviewCard key={review.id} review={review} />)}</div></section>
    </main>
  );
}
