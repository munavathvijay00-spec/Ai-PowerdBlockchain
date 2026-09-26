/**
 * API client for the Blockchain Intelligence backend.
 * Centralizes all HTTP calls to the API.
 */

const API_BASE = '/api';

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  getStats: () => request('/stats'),
  getTransactions: (limit = 20) => request(`/transactions?limit=${limit}`),
  getFlagged: (minScore = 20) => request(`/flagged?min_score=${minScore}`),
  getTransaction: (hash) => request(`/transactions/${hash}`),
};