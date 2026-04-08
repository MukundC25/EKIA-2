import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 2-minute timeout for LLM inference
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail?.message || error.response?.data?.detail || error.message;
    console.error('[API] Error:', msg);
    return Promise.reject(error);
  }
);

export const debugError = (payload) =>
  api.post('/api/debug', payload).then((r) => r.data);

export const getFullGraph = (limit = 100) =>
  api.get('/api/graph/', { params: { limit } }).then((r) => r.data);

export const searchGraph = (error, depth = 2) =>
  api.get('/api/graph/search', { params: { error, depth } }).then((r) => r.data);

export const getGraphStats = () =>
  api.get('/api/graph/stats').then((r) => r.data);

export const getHealth = () =>
  api.get('/health').then((r) => r.data);

export const getDebugHistory = () =>
  api.get('/api/debug/history').then((r) => r.data);

export default api;
