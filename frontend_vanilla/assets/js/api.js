const API_URL = 'http://127.0.0.1:8000/v1';

const api = {
    async get(endpoint) {
        const token = localStorage.getItem('spotify_dwh_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        
        const response = await fetch(`${API_URL}${endpoint}`, { headers });
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        return response.json();
    },
    
    async post(endpoint, body = {}) {
        const token = localStorage.getItem('spotify_dwh_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body)
        });
        if (!response.ok) throw new Error(`Error: ${response.status}`);
        return response.json();
    }
};

const spotifyApi = {
    getLoginUrl: () => api.get('/auth/login'),
    callback: (code, state) => api.get(`/auth/callback?code=${code}&state=${state}`),
    getProfile: () => api.get('/profile/me'),
    getTopArtists: () => api.get('/artists/top'),
    getTopTracks: () => api.get('/tracks/top'),
    getHistory: () => api.get('/history/recently-played'),
    runEtl: () => api.post('/etl/run'),
    getEtlStatus: () => api.get('/etl/status'),
};
