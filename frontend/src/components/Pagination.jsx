import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;
  const firstPage = Math.max(1, Math.min(totalPages - 4, page - 2));
  const pages = Array.from({ length: Math.min(totalPages, 5) }, (_, index) => firstPage + index);
  return <nav className="pagination" aria-label="Pagination"><button type="button" onClick={() => onPageChange(page - 1)} disabled={page <= 1} aria-label="Previous page"><ChevronLeftIcon className="h-4 w-4" /></button>{pages.map((item) => <button key={item} type="button" className={item === page ? 'active' : ''} onClick={() => onPageChange(item)} aria-label={`Page ${item}`}>{item}</button>)}<button type="button" onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} aria-label="Next page"><ChevronRightIcon className="h-4 w-4" /></button></nav>;
}
