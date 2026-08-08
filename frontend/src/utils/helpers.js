// ===================================================================
// Utility Helpers — Customer Review Intelligence Platform
// ===================================================================

/**
 * Returns the color class for a sentiment value.
 */
export const getSentimentColor = (sentiment) => {
  const s = (sentiment || '').toLowerCase();
  if (s === 'positive') return { bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' };
  if (s === 'negative') return { bg: 'bg-red-500/15', text: 'text-red-400', border: 'border-red-500/30', dot: 'bg-red-400' };
  return { bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-400' };
};

/**
 * Returns the hex color for a sentiment value (for charts).
 */
export const getSentimentHex = (sentiment) => {
  const s = (sentiment || '').toLowerCase();
  if (s === 'positive') return '#34d399';
  if (s === 'negative') return '#f87171';
  return '#fbbf24';
};

/**
 * Generates an array of filled/empty star indicators for a given rating.
 */
export const getStars = (rating, maxStars = 5) => {
  const r = Math.round(parseFloat(rating) || 0);
  return Array.from({ length: maxStars }, (_, i) => i < r);
};

/**
 * Truncates text to a max length with ellipsis.
 */
export const truncateText = (text, maxLength = 150) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trimEnd() + '…';
};

/**
 * Formats a number with commas (e.g., 306316 → "306,316").
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0';
  return Number(num).toLocaleString('en-US');
};

/**
 * Formats a percentage value to fixed decimals.
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${Number(value).toFixed(decimals)}%`;
};

/**
 * Formats a rating to one decimal (e.g., 4.2).
 */
export const formatRating = (rating) => {
  if (rating === null || rating === undefined) return '0.0';
  return Number(rating).toFixed(1);
};

/**
 * Returns a confidence label based on a confidence score.
 */
export const getConfidenceLabel = (confidence) => {
  if (confidence >= 0.9) return { label: 'Very High', color: 'text-emerald-400' };
  if (confidence >= 0.75) return { label: 'High', color: 'text-emerald-300' };
  if (confidence >= 0.6) return { label: 'Moderate', color: 'text-amber-400' };
  if (confidence >= 0.4) return { label: 'Low', color: 'text-amber-300' };
  return { label: 'Very Low', color: 'text-red-400' };
};

/**
 * Debounce utility.
 */
export const debounce = (fn, delay = 300) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
};

/**
 * Generates a rating distribution array from a rating distribution object.
 */
export const formatRatingDistribution = (distribution) => {
  if (!distribution) return [];
  return [1, 2, 3, 4, 5].map((star) => ({
    star: `${star}★`,
    count: distribution[star] || distribution[String(star)] || 0,
  }));
};

/**
 * Generates sentiment distribution array for Recharts.
 */
export const formatSentimentDistribution = (distribution) => {
  if (!distribution) return [];
  return [
    { name: 'Positive', value: distribution.Positive || 0, fill: '#34d399' },
    { name: 'Neutral', value: distribution.Neutral || 0, fill: '#fbbf24' },
    { name: 'Negative', value: distribution.Negative || 0, fill: '#f87171' },
  ];
};

/**
 * Classname merge helper.
 */
export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};
