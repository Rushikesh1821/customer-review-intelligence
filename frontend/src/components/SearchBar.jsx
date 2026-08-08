import { useEffect, useRef, useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export default function SearchBar({ value = '', onSearch, placeholder = 'Search…', debounceMs = 350 }) {
  const [localValue, setLocalValue] = useState(value);
  const timerRef = useRef(null);
  useEffect(() => { setLocalValue(value); }, [value]);
  useEffect(() => () => window.clearTimeout(timerRef.current), []);
  const handleChange = (event) => { const next = event.target.value; setLocalValue(next); window.clearTimeout(timerRef.current); timerRef.current = window.setTimeout(() => onSearch?.(next), debounceMs); };
  return <div className="search-field"><MagnifyingGlassIcon /><input className="input" value={localValue} onChange={handleChange} placeholder={placeholder} aria-label={placeholder} /></div>;
}
