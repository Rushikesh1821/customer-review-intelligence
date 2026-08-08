import axios from 'axios';

// ===================================================================
// Axios Instance — Customer Review Intelligence Platform API Client
// ===================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Request Interceptor ---
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Response Interceptor ---
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);

    return Promise.reject({
      message,
      status: error.response?.status || 500,
      data: error.response?.data || null,
    });
  }
);

// ===================================================================
// API Functions
// ===================================================================

/**
 * GET /dashboard — Executive dashboard metrics
 */
export const getDashboard = () => {
  return api.get('/dashboard');
};

/**
 * POST /predict-sentiment — Predict sentiment for review text
 */
export const predictSentiment = (text) => {
  return api.post('/predict-sentiment', { text });
};

/**
 * POST /ask-ai — Ask a question using RAG + Gemini AI
 */
export const askAI = (question, product = null, topK = 5) => {
  return api.post('/ask-ai', {
    question,
    product: product || null,
    top_k: topK,
  });
};

/**
 * GET /products — List products with search and pagination
 */
export const getProducts = (search = '', limit = 100, offset = 0) => {
  return api.get('/products', {
    params: { search, limit, offset },
  });
};

/**
 * GET /product/:name — Detailed product analytics
 */
export const getProductDetails = (productName) => {
  return api.get(`/product/${encodeURIComponent(productName)}`);
};

/**
 * GET /reviews — Review explorer with search, filters, pagination
 */
export const exploreReviews = ({
  page = 1,
  pageSize = 20,
  search = '',
  product = '',
  sentiment = '',
  rating = null,
  isSemantic = false,
} = {}) => {
  const params = {
    page,
    page_size: pageSize,
    search,
    product,
    sentiment,
    is_semantic: isSemantic,
  };
  if (rating !== null && rating !== '' && rating !== 'all') {
    params.rating = parseFloat(rating);
  }
  return api.get('/reviews', { params });
};

/**
 * POST /compare-products — Compare two products head-to-head
 */
export const compareProducts = (productA, productB) => {
  return api.post('/compare-products', {
    product_a: productA,
    product_b: productB,
  });
};

/**
 * GET /analytics — Full analytics overview
 */
export const getAnalytics = () => {
  return api.get('/analytics');
};

/**
 * GET / — Health check
 */
export const healthCheck = () => {
  return api.get('/');
};

export default api;
