import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/v1';

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor para añadir el token JWT a todas las peticiones
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('spotify_dwh_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const spotifyApi = {
  // Auth
  getLoginUrl: () => api.get('/auth/login'),
  callback: (code: string, state: string) => api.get(`/auth/callback?code=${code}&state=${state}`),
  
  // Profile
  getProfile: () => api.get('/profile/me'),
  
  // Data
  getTopArtists: () => api.get('/artists/top'),
  getTopTracks: () => api.get('/tracks/top'),
  getHistory: () => api.get('/history/recently-played'),
  
  // ETL
  runEtl: () => api.post('/etl/run'),
  getEtlStatus: () => api.get('/etl/status'),
};

export default api;
