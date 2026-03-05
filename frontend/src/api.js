const BASE = import.meta.env.VITE_API_URL || '/api';

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  if (token) localStorage.setItem('token', token);
  else localStorage.removeItem('token');
}

export function getStoredUser() {
  const raw = localStorage.getItem('user');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  if (user) localStorage.setItem('user', JSON.stringify(user));
  else localStorage.removeItem('user');
}

export function logout() {
  setToken(null);
  setStoredUser(null);
}

async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || res.statusText || 'Request failed');
  }
  return data;
}

export const api = {
  async signup(email, password) {
    const data = await request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    setStoredUser(data.user);
    return data;
  },

  async login(email, password) {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    setStoredUser(data.user);
    return data;
  },

  async me() {
    return request('/auth/me');
  },

  async myPlans() {
    return request('/users/me/plans');
  },

  async generatePlan(body) {
    return request('/generate-plan', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  async getPlan(id) {
    return request(`/plans/${id}`);
  },

  async getPlanWithDays(id) {
    return request(`/plans/${id}/with-days`);
  },
};

export { getToken, setToken };
