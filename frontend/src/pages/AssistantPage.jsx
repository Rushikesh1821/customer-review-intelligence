import { useEffect, useState } from 'react';
import { PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { askAI, getProducts } from '../services/api';
import { useApi } from '../hooks/useApi';
import ErrorState from '../components/ErrorState';
import PageHeader from '../components/PageHeader';
import ReviewCard from '../components/ReviewCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

const prompts = ['What are the biggest customer complaints?', 'Why are customers unhappy with this product?', 'What do customers like most?', 'What are the main battery problems?'];

export default function AssistantPage() {
  const [question, setQuestion] = useState('');
  const [product, setProduct] = useState('');
  const [products, setProducts] = useState([]);
  const { data: answer, loading, error, execute } = useApi(askAI);
  useEffect(() => { getProducts('', 1000).then((response) => setProducts(response.products || [])).catch(() => undefined); }, []);
  const submit = async (event) => { event.preventDefault(); if (!question.trim()) return toast.error('Enter a question about customer feedback.'); try { await execute(question.trim(), product || null, 6); } catch { toast.error('The AI assistant could not complete that request.'); } };

  return <main className="page"><PageHeader title="AI Review Assistant" description="Understand your customers using natural language, grounded in retrieved customer reviews." /><section className="surface surface-padded mx-auto max-w-4xl"><div className="mb-6 text-center"><span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><SparklesIcon className="h-5 w-5" /></span><h2 className="mt-3 text-lg font-bold text-slate-900">Ask about your customer reviews</h2><p className="mt-1 text-sm text-slate-500">Ask one clear question. Add a product to narrow the review evidence.</p></div><form onSubmit={submit}><textarea className="textarea" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about your customer reviews…" maxLength={1000} rows={4} /><div className="mt-3 flex flex-col gap-3 sm:flex-row"><input className="input flex-1" value={product} onChange={(event) => setProduct(event.target.value)} list="assistant-product-list" placeholder="All products (optional)" /><datalist id="assistant-product-list">{products.map((item) => <option key={item.product_name} value={item.product_name} />)}</datalist><button type="submit" className="button-primary" disabled={loading}>{loading ? <><LoadingSpinner size="sm" />Analyzing feedback…</> : <><PaperAirplaneIcon className="h-4 w-4" />Ask AI</>}</button></div></form><div className="mt-4 flex flex-wrap justify-center gap-2">{prompts.map((prompt) => <button key={prompt} type="button" className="button-quiet border border-slate-200" onClick={() => setQuestion(prompt)}>{prompt}</button>)}</div></section>{error && !loading && <div className="mt-5"><ErrorState title="The assistant could not answer" description="Please check your question and try again." onRetry={() => execute(question, product || null, 6).catch(() => undefined)} /></div>}{answer && !loading && <section className="mx-auto mt-5 max-w-4xl"><div className="ai-panel"><div className="ai-panel-head"><h2><SparklesIcon className="h-4 w-4" />AI generated answer</h2><span className="text-xs font-semibold text-indigo-600">Based on {answer.review_count || 0} reviews</span></div><div className="ai-panel-body">{answer.answer}</div></div><div className="mt-5"><div className="section-heading"><div><h2>Retrieved review sources</h2><p>Evidence used to ground the answer.</p></div></div><div className="review-list">{answer.retrieved_reviews?.map((review, index) => <ReviewCard key={review.id || index} review={review} />)}</div></div></section>}</main>;
}
