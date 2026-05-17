"use client";

import { useEffect, useState } from "react";
import { Music } from "lucide-react";
import { spotifyApi } from "@/lib/api";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    try {
      const response = await spotifyApi.getLoginUrl();
      // Redirigir a la URL de Spotify devuelta por el backend
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Error al iniciar sesión:", error);
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-[#121212] text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex flex-col gap-8 text-center">
        <div className="bg-[#1DB954] p-4 rounded-full animate-bounce">
          <Music size={48} color="black" />
        </div>
        
        <h1 className="text-6xl font-black tracking-tighter">
          MI <span className="text-[#1DB954]">SPOTIFY</span> WRAPPED
        </h1>
        
        <p className="text-gray-400 max-w-md text-lg">
          Conecta tu cuenta de Spotify para construir tu propio Data Warehouse personal y analizar tus hábitos musicales.
        </p>

        <button 
          onClick={handleLogin}
          disabled={loading}
          className="btn-spotify flex items-center gap-2 text-lg px-12 py-4"
        >
          {loading ? "Cargando..." : "CONECTAR CON SPOTIFY"}
        </button>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl text-left">
          <div className="glass-card">
            <h3 className="text-[#1DB954] font-bold mb-2">ETL Automático</h3>
            <p className="text-sm text-gray-400">Extrae tus datos de Spotify y cárgalos en un Galaxy Schema de PostgreSQL.</p>
          </div>
          <div className="glass-card">
            <h3 className="text-[#1DB954] font-bold mb-2">Carga Incremental</h3>
            <p className="text-sm text-gray-400">Sincroniza solo lo nuevo desde tu última escucha.</p>
          </div>
          <div className="glass-card">
            <h3 className="text-[#1DB954] font-bold mb-2">Análisis EDA</h3>
            <p className="text-sm text-gray-400">Genera insights profundos sobre tus géneros y artistas dominantes.</p>
          </div>
        </div>
      </div>
      
      {/* Background decoration */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 opacity-20">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#1DB954] blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600 blur-[120px]"></div>
      </div>
    </main>
  );
}
