"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { spotifyApi } from "@/lib/api";

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (code && state) {
      handleCallback(code, state);
    } else {
      setError("Faltan parámetros en el callback de Spotify.");
    }
  }, [searchParams]);

  const handleCallback = async (code: string, state: string) => {
    try {
      const response = await spotifyApi.callback(code, state);
      const { access_token } = response.data;
      
      // Guardar JWT en localStorage
      localStorage.setItem("spotify_dwh_token", access_token);
      
      // Redirigir al dashboard
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Error en el callback:", err);
      setError(err.response?.data?.detail || "Error al autenticar con el backend.");
    }
  };

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#121212] text-white p-6 text-center">
        <div className="max-w-md">
          <h2 className="text-2xl font-bold text-red-500 mb-4">Error de Autenticación</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button 
            onClick={() => router.push("/")}
            className="btn-spotify"
          >
            VOLVER AL INICIO
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#121212] text-white gap-6">
      <Loader2 size={48} className="text-[#1DB954] animate-spin" />
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Finalizando conexión...</h2>
        <p className="text-gray-400">Estamos sincronizando tu cuenta con el Data Warehouse.</p>
      </div>
    </div>
  );
}
