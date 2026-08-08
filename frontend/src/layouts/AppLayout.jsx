import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { BellIcon } from '@heroicons/react/24/outline';
import Sidebar from '../components/Sidebar';

const pageContext = {
  '/': ['Workspace', 'Overview'],
  '/ai-assistant': ['Intelligence', 'AI Assistant'],
  '/reviews': ['Intelligence', 'Customer Reviews'],
  '/products': ['Catalog', 'Products'],
  '/analytics': ['Intelligence', 'Analytics'],
  '/sentiment': ['Tools', 'Sentiment Analysis'],
  '/settings': ['Workspace', 'Settings'],
};

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const context = location.pathname.startsWith('/products/')
    ? ['Catalog', 'Product Insights']
    : pageContext[location.pathname] || ['Customer Review Intelligence', 'Workspace'];

  return (
    <div className="app-shell">
      <Sidebar collapsed={collapsed} onCollapseChange={setCollapsed} />
      <main className={`app-main ${collapsed ? 'is-collapsed' : ''}`}>
        <header className="app-header">
          <div className="header-context"><p>{context[0]}</p><h2>{context[1]}</h2></div>
          <div className="header-actions">
            <span className="header-status"><span className="status-dot" />Data connected</span>
            <button type="button" className="header-icon-button" aria-label="Notifications"><BellIcon className="h-4 w-4" /></button>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
