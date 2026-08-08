import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Bars3Icon,
  BoltIcon,
  ChartBarIcon,
  ChatBubbleBottomCenterTextIcon,
  ChevronLeftIcon,
  Cog6ToothIcon,
  CubeIcon,
  MagnifyingGlassIcon,
  SparklesIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { path: '/', label: 'Overview', icon: ChartBarIcon },
  { path: '/ai-assistant', label: 'AI Assistant', icon: SparklesIcon },
  { path: '/reviews', label: 'Reviews', icon: MagnifyingGlassIcon },
  { path: '/products', label: 'Products', icon: CubeIcon },
  { path: '/analytics', label: 'Analytics', icon: ChartBarIcon },
  { path: '/sentiment', label: 'Sentiment', icon: ChatBubbleBottomCenterTextIcon },
];

export default function Sidebar({ collapsed, onCollapseChange }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const compact = collapsed && !mobileOpen;

  return (
    <>
      {mobileOpen && <button type="button" className="mobile-nav-backdrop" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
      <aside className={`app-sidebar ${compact ? 'is-collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark"><BoltIcon className="h-5 w-5" /></div>
          {!compact && <div className="brand-copy"><strong>Review Intelligence</strong><span>Customer feedback platform</span></div>}
          <button type="button" className="sidebar-collapse" onClick={() => onCollapseChange(!collapsed)} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}><ChevronLeftIcon className={`h-4 w-4 transition-transform ${collapsed ? 'rotate-180' : ''}`} /></button>
          <button type="button" className="sidebar-collapse lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><XMarkIcon className="h-4 w-4" /></button>
        </div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {!compact && <p className="sidebar-label">Workspace</p>}
          {navigation.map(({ path, label, icon: Icon }) => (
            <NavLink key={path} to={path} end={path === '/'} onClick={() => setMobileOpen(false)} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} title={compact ? label : undefined}>
              <Icon />{!compact && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <NavLink to="/settings" onClick={() => setMobileOpen(false)} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} title={compact ? 'Settings' : undefined}><Cog6ToothIcon />{!compact && <span>Settings</span>}</NavLink>
          <div className="sidebar-profile"><span className="profile-avatar">RI</span>{!compact && <div className="profile-copy"><strong>Review workspace</strong><span>Analytics team</span></div>}</div>
        </div>
      </aside>
      <button type="button" className="mobile-nav-trigger fixed left-4 top-[15px] z-30" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Bars3Icon className="h-5 w-5" /></button>
    </>
  );
}
