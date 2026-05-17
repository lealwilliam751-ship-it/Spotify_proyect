const API_BASE_URL = "http://127.0.0.1:8000";

export const spotifyApi = {
    getHeaders() {
        const token = localStorage.getItem("spotify_dwh_token");
        return {
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {})
        };
    },

    async handleResponse(response) {
        if (response.status === 401) {
            localStorage.removeItem("spotify_dwh_token");
            window.location.href = "/";
            throw new Error("Unauthorized");
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Error en la petición");
        }
        return response.json();
    },

    async login() {
        // Redirect the browser directly to backend - it will redirect to Spotify
        window.location.href = `${API_BASE_URL}/v1/auth/login`;
    },

    async getProfile() {
        const res = await fetch(`${API_BASE_URL}/v1/profile/me`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async getTopArtists() {
        const res = await fetch(`${API_BASE_URL}/v1/artists/top`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async getTopTracks() {
        const res = await fetch(`${API_BASE_URL}/v1/tracks/top`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async getETLStatus() {
        const res = await fetch(`${API_BASE_URL}/v1/etl/status`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async getStats() {
        const res = await fetch(`${API_BASE_URL}/v1/history/stats`, { headers: this.getHeaders() });
        return this.handleResponse(res);
    },

    async runETL() {
        const res = await fetch(`${API_BASE_URL}/v1/etl/run`, { 
            method: 'POST',
            headers: this.getHeaders() 
        });
        return this.handleResponse(res);
    }
};
