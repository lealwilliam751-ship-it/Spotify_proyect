"use client";

import { useEffect, useState } from "react";
import { RefreshCcw, CheckCircle2, XCircle, Clock, Play } from "lucide-react";
import { spotifyApi } from "@/lib/api";

export default function EtlPage() {
  const [etlHistory, setEtlHistory] = useState([]);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEtlStatus();
  }, []);

  const fetchEtlStatus = async () => {
    try {
      const response = await spotifyApi.getEtlStatus();
      setEtlHistory(response.data);
    } catch (err) {
      console.error("Error fetching ETL status:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunEtl = async () => {
    setRunning(true);
    try {
      await spotifyApi.runEtl();
      // Esperar un momento y refrescar
      setTimeout(fetchEtlStatus, 2000);
    } catch (err) {
      console.error("Error running ETL:", err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* Sidebar (Copy from Dashboard for simplicity or use a layout) */}
      <aside className="w-64 bg-black p-6 border-r border-white/10">
        <Link href="/dashboard" className="flex items-center gap-2 text-[#1DB954] font-black text-xl mb-10">
          <Music size={32} /> SPOTIFY DWH
        </Link>
        <nav className="flex flex-col gap-2">
          <Link href="/dashboard" className="nav-item">Dashboard</Link>
          <Link href="/profile" className="nav-item">Mi Perfil</Link>
          <Link href="/etl" className="nav-item active">Pipeline ETL</Link>
        </nav>
      </aside>

      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-bold">Pipeline ETL</h1>
            <p className="text-gray-400">Orquesta la extracción, transformación y carga incremental.</p>
          </div>
          <button 
            onClick={handleRunEtl}
            disabled={running}
            className={`flex items-center gap-2 px-6 py-3 rounded-full font-bold transition-all ${
              running ? "bg-gray-700 text-gray-400" : "bg-[#1DB954] text-black hover:scale-105"
            }`}
          >
            {running ? <RefreshCcw className="animate-spin" /> : <Play fill="black" />}
            {running ? "EJECUTANDO..." : "SINCRONIZAR AHORA"}
          </button>
        </header>

        <section className="glass-card mb-10">
          <h2 className="text-xl font-bold mb-6">Historial de Auditoría (etl_audit)</h2>
          <div className="overflow-hidden border border-white/10 rounded-lg">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-white/5 text-gray-400">
                  <th className="p-4">ID</th>
                  <th className="p-4">Inicio</th>
                  <th className="p-4">Estado</th>
                  <th className="p-4">Duración</th>
                  <th className="p-4">Nuevos Registros</th>
                </tr>
              </thead>
              <tbody>
                {etlHistory.map((audit: any) => (
                  <tr key={audit.audit_id} className="border-t border-white/5 hover:bg-white/5">
                    <td className="p-4 font-mono text-gray-500">#{audit.audit_id}</td>
                    <td className="p-4">{new Date(audit.started_at).toLocaleString()}</td>
                    <td className="p-4">
                      <span className={`flex items-center gap-1 font-bold ${
                        audit.status === 'COMPLETED' ? 'text-[#1DB954]' : 
                        audit.status === 'FAILED' ? 'text-red-500' : 'text-yellow-500'
                      }`}>
                        {audit.status === 'COMPLETED' && <CheckCircle2 size={16} />}
                        {audit.status === 'FAILED' && <XCircle size={16} />}
                        {audit.status === 'RUNNING' && <RefreshCcw size={16} className="animate-spin" />}
                        {audit.status}
                      </span>
                    </td>
                    <td className="p-4 flex items-center gap-1 text-gray-400">
                      <Clock size={14} /> {audit.duration_ms || '--'}ms
                    </td>
                    <td className="p-4 text-gray-300">
                      Artistas: {audit.artists_new} | Canciones: {audit.tracks_new} | Historial: {audit.history_new}
                    </td>
                  </tr>
                ))}
                {etlHistory.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-10 text-center text-gray-500 italic">
                      No hay ejecuciones registradas. Haz clic en "Sincronizar Ahora" para comenzar.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

// Re-using Sidebar components normally involves moving them to a separate file, 
// but for this implementation I'll keep it simple.
import { Music } from "lucide-react";
