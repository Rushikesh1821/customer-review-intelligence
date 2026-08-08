import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const SentimentPage = lazy(() => import('./pages/SentimentPage'));
const AssistantPage = lazy(() => import('./pages/AssistantPage'));
const ProductsPage = lazy(() => import('./pages/ProductsPage'));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'));
const ReviewsPage = lazy(() => import('./pages/ExplorerPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

function NotFoundPage() {
  return <Navigate to="/" replace />;
}

function RoutedPage({ Component }) {
  return (
    <Suspense fallback={<div className="page flex min-h-80 items-center justify-center text-sm text-slate-500">Loading workspace…</div>}>
      <Component />
    </Suspense>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<RoutedPage Component={DashboardPage} />} />
        <Route path="ai-assistant" element={<RoutedPage Component={AssistantPage} />} />
        <Route path="assistant" element={<Navigate to="/ai-assistant" replace />} />
        <Route path="reviews" element={<RoutedPage Component={ReviewsPage} />} />
        <Route path="explorer" element={<Navigate to="/reviews" replace />} />
        <Route path="products" element={<RoutedPage Component={ProductsPage} />} />
        <Route path="products/:productId" element={<RoutedPage Component={ProductDetailPage} />} />
        <Route path="analytics" element={<RoutedPage Component={AnalyticsPage} />} />
        <Route path="sentiment" element={<RoutedPage Component={SentimentPage} />} />
        <Route path="settings" element={<RoutedPage Component={SettingsPage} />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
