"use client";

import { useEffect, useState } from "react";
import { LayoutDashboard, Users, Music, History, RefreshCcw, User } from "lucide-react";
import Link from "next/link";
import { spotifyApi } from "@/lib/api";

export default function DashboardPage() {
  const [profile, setProfile] = useState<any>(null);
  const [topArtists, setTopArtists] = useState([]);
  const [topTracks, setTopTracks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [pRes, aRes, tRes] = await Promise.all([
        spotifyApi.getProfile(),
        spotifyApi.getTopArtists(),
        spotifyApi.getTopTracks(),
      ]);
      setProfile(pRes.data);
      setTopArtists(aRes.data);
      setTopTracks(tRes.data);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-black text-white">Cargando Dashboard...</div>;
  }

  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-[#000000] p-6 flex flex-col gap-8 border-r border-white/10">
        <div className="flex items-center gap-2 text-[#1DB954] font-black text-xl">
          <Music size={32} />
          <span>SPOTIFY DWH</span>
        </div>
        
        <nav className="flex flex-col gap-2">
          <Link href="/dashboard" className="nav-item active">
            <LayoutDashboard size={20} /> Dashboard
          </Link>
          <Link href="/profile" className="nav-item">
            <User size={20} /> Mi Perfil
          </Link>
          <Link href="/etl" className="nav-item">
            <RefreshCcw size={20} /> Pipeline ETL
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-bold">¡Hola, {profile?.display_name}!</h1>
            <p className="text-gray-400">Este es el estado actual de tu Data Warehouse personal.</p>
          </div>
          <div className="flex items-center gap-4 bg-white/5 p-2 pr-6 rounded-full border border-white/10">
            <div className="w-10 h-10 bg-[#1DB954] rounded-full flex items-center justify-center font-bold text-black">
              {profile?.display_name?.[0]}
            </div>
            <span className="font-medium">{profile?.display_name}</span>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
          <div className="glass-card flex flex-col gap-2">
            <span className="text-gray-400 text-sm">Artistas en DWH</span>
            <span className="text-4xl font-bold">{topArtists.length}</span>
          </div>
          <div className="glass-card flex flex-col gap-2">
            <span className="text-gray-400 text-sm">Canciones en DWH</span>
            <span className="text-4xl font-bold">{topTracks.length}</span>
          </div>
          <div className="glass-card flex flex-col gap-2">
            <span className="text-gray-400 text-sm">País Spotify</span>
            <span className="text-4xl font-bold">{profile?.country}</span>
          </div>
          <div className="glass-card flex flex-col gap-2 border-[#1DB954]/30">
            <span className="text-gray-400 text-sm">Status ETL</span>
            <span className="text-4xl font-bold text-[#1DB954]">OK</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Top Artists Widget */}
          <section>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Users size={20} className="text-[#1DB954]" /> Mis Artistas Top (DWH)
            </h2>
            <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/10 text-gray-400 text-sm">
                    <th className="p-4">#</th>
                    <th className="p-4">Nombre</th>
                    <th className="p-4">Popularidad</th>
                  </tr>
                </thead>
                <tbody>
                  {topArtists.slice(0, 5).map((artist: any, i) => (
                    <tr key={artist.spotify_id} className="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                      <td className="p-4 text-gray-500">{i + 1}</td>
                      <td className="p-4 font-medium">{artist.name}</td>
                      <td className="p-4">
                        <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
                          <div 
                            className="bg-[#1DB954] h-full" 
                            style={{ width: `${artist.popularity}%` }}
                          ></div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Top Tracks Widget */}
          <section>
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Music size={20} className="text-[#1DB954]" /> Mis Canciones Top (DWH)
            </h2>
            <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/10 text-gray-400 text-sm">
                    <th className="p-4">#</th>
                    <th className="p-4">Canción</th>
                    <th className="p-4">Álbum</th>
                  </tr>
                </thead>
                <tbody>
                  {topTracks.slice(0, 5).map((track: any, i) => (
                    <tr key={track.spotify_id} className="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
                      <td className="p-4 text-gray-500">{i + 1}</td>
                      <td className="p-4 font-medium">{track.name}</td>
                      <td className="p-4 text-gray-400 text-sm">{track.album_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
