import { useState, useEffect } from "react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";
import {
  Music, LogOut, Zap, RefreshCw, CheckCircle, XCircle, Loader2,
  Database, Layers, Star, TrendingUp, Activity, User
} from "lucide-react";
import { spotifyApi } from "./api.js";

// ─── MOCK DATA (For Charts) ──────────────────────────────────────────────────
const HOURLY = [
  { h: "00", v: 8 }, { h: "04", v: 3 }, { h: "07", v: 28 }, { h: "08", v: 45 },
  { h: "10", v: 32 }, { h: "12", v: 41 }, { h: "14", v: 29 }, { h: "17", v: 52 },
  { h: "18", v: 67 }, { h: "19", v: 78 }, { h: "20", v: 85 }, { h: "21", v: 92 },
  { h: "22", v: 74 }, { h: "23", v: 45 },
];
const WEEKLY = [
  { d: "Lun", v: 145 }, { d: "Mar", v: 132 }, { d: "Mié", v: 178 },
  { d: "Jue", v: 159 }, { d: "Vie", v: 267 }, { d: "Sáb", v: 312 }, { d: "Dom", v: 289 },
];
const GENRES = [
  { g: "Reggaetón", v: 38 }, { g: "R&B", v: 22 }, { g: "Trap", v: 18 },
  { g: "Pop", v: 14 }, { g: "Hip-Hop", v: 8 },
];

// ─── COUNT-UP HOOK ────────────────────────────────────────────────────────
function useCountUp(target, delay = 0) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!target) return;
    const timeout = setTimeout(() => {
      let start = 0;
      const step = Math.max(1, target / 50);
      const id = setInterval(() => {
        start += step;
        if (start >= target) { setVal(target); clearInterval(id); }
        else setVal(Math.floor(start));
      }, 16);
      return () => clearInterval(id);
    }, delay);
    return () => clearTimeout(timeout);
  }, [target, delay]);
  return val;
}

// ─── STYLES ──────────────────────────────────────────────────────────────────
const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

  :root {
    --bg-0: #0a0703;
    --bg-1: #0d0a05;
    --bg-2: #151108;
    --bg-3: #1d1809;
    --gold-dark: #7d6b3d;
    --gold-med: #a89060;
    --gold-main: #c9a84c;
    --gold-light: #e8c467;
    --gold-bright: #f5dfa0;
    --text-primary: #f0e2bc;
    --text-secondary: #a89060;
    --text-tertiary: #6b5535;
    --border-color: rgba(201, 168, 76, 0.15);
    --border-hover: rgba(201, 168, 76, 0.3);
    --glow-soft: rgba(201, 168, 76, 0.3);
    --glow-bright: rgba(232, 196, 103, 0.5);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { background: var(--bg-0); font-family: 'Rajdhani', sans-serif; color: var(--text-primary); line-height: 1.5; }

  @keyframes fade-in-up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes fade-in-down { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes slide-in-right { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
  @keyframes scale-in { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
  @keyframes shimmer { 0% { background-position: -400% center; } 100% { background-position: 400% center; } }
  @keyframes rotate-ring { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  @keyframes bar-grow { from { width: 0%; } to { width: var(--bar-width); } }
  @keyframes pulse-dot { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--gold-dark); border-radius: 4px; opacity: 0.5; }
  ::-webkit-scrollbar-thumb:hover { background: var(--gold-med); opacity: 0.8; }

  .card {
    background: linear-gradient(135deg, rgba(20, 16, 8, 0.95) 0%, rgba(13, 10, 5, 0.98) 100%);
    border: 1px solid var(--border-color); border-radius: 4px; position: relative; overflow: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(232, 196, 103, 0.3), transparent); pointer-events: none; }
  .card:hover { border-color: var(--border-hover); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); }

  .btn-primary {
    background: linear-gradient(135deg, var(--gold-main) 0%, var(--gold-light) 100%);
    color: #0a0703; border: none; padding: 12px 32px; border-radius: 4px; font-family: 'Cinzel', serif; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.05em; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(201, 168, 76, 0.2);
  }
  .btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(201, 168, 76, 0.4); }
  .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

  .page-title { font-family: 'Cinzel', serif; font-size: 2rem; font-weight: 400; letter-spacing: 0.02em; color: var(--text-primary); margin-bottom: 8px; }
  .subtitle { font-size: 0.9rem; color: var(--text-secondary); font-weight: 300; }
  .stat-value { font-family: 'Cinzel', serif; font-size: 2.2rem; font-weight: 700; color: var(--gold-light); letter-spacing: 0.02em; }
  .accent-bar { width: 3px; height: 24px; background: linear-gradient(180deg, var(--gold-main), transparent); border-radius: 2px; }

  .status-completed { background: rgba(201, 168, 76, 0.08); border: 1px solid rgba(201, 168, 76, 0.25); color: var(--gold-light); }
  .status-failed { background: rgba(180, 50, 50, 0.08); border: 1px solid rgba(180, 50, 50, 0.25); color: #ff6b6b; }
  .status-running { background: rgba(201, 168, 76, 0.05); border: 1px solid rgba(201, 168, 76, 0.15); color: var(--gold-main); }
`;

// ─── LOGIN PAGE ──────────────────────────────────────────────────────────────
function LoginPage() {
  const onLogin = async () => {
    await spotifyApi.login();
  };

  return (
    <div style={{
      minHeight: "100vh", background: "linear-gradient(135deg, #0a0703 0%, #151108 50%, #0a0703 100%)",
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "40px", padding: "20px", animation: "fade-in-up 0.6s ease forwards"
    }}>
      <div style={{ textAlign: "center", animation: "fade-in-up 0.6s 0.1s ease forwards", opacity: 0 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "16px", marginBottom: "24px" }}>
          <Music size={48} color="#c9a84c" strokeWidth={1.5} />
          <h1 style={{ fontFamily: "'Cinzel', serif", fontSize: "2.5rem", fontWeight: 400, color: "#f0e2bc", letterSpacing: "0.02em" }}>Spotify<br />DWH</h1>
        </div>
        <p style={{ fontSize: "0.95rem", color: "#a89060", maxWidth: "300px", lineHeight: 1.6 }}>Tu Data Warehouse personal de Spotify. Conecta, extrae y visualiza tus hábitos musicales.</p>
      </div>
      <button onClick={onLogin} className="btn-primary" style={{ padding: "16px 48px", fontSize: "1rem", animation: "fade-in-up 0.6s 0.2s ease forwards", opacity: 0 }}>
        Conectar con Spotify
      </button>
    </div>
  );
}

// ─── CALLBACK PAGE ───────────────────────────────────────────────────────────
function CallbackPage({ onDone }) {
  useEffect(() => {
    const timer = setTimeout(onDone, 2000);
    return () => clearTimeout(timer);
  }, [onDone]);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-0)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "24px" }}>
      <Loader2 size={48} color="#c9a84c" style={{ animation: "rotate-ring 2s linear infinite" }} />
      <p style={{ fontSize: "0.9rem", color: "#a89060" }}>Autenticando...</p>
    </div>
  );
}

// ─── SIDEBAR ─────────────────────────────────────────────────────────────────
function Sidebar({ page, setPage, user, onLogout }) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: Activity },
    { id: "profile", label: "Mi Perfil", icon: User },
    { id: "etl", label: "Pipeline ETL", icon: Zap },
  ];

  return (
    <aside style={{
      width: "280px", background: "linear-gradient(180deg, rgba(13, 10, 5, 0.95) 0%, rgba(10, 7, 3, 0.98) 100%)",
      borderRight: "1px solid rgba(201, 168, 76, 0.1)", display: "flex", flexDirection: "column", padding: "32px 24px", gap: "32px", overflow: "hidden"
    }}>
      <div style={{ animation: "fade-in-down 0.5s ease forwards" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="#c9a84c" style={{ flexShrink: 0 }}>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.59 14.42c-.18.29-.56.38-.85.2-2.37-1.45-5.37-1.78-8.89-1.02-.33.07-.67-.14-.74-.48-.07-.33.14-.67.48-.74 3.86-.83 7.16-.45 9.81 1.18.29.18.38.56.2.86zm1.23-2.72c-.23.37-.71.49-1.08.26-2.72-1.67-6.87-2.16-10.08-1.18-.41.13-.85-.11-.97-.52-.13-.41.11-.85.52-.97 3.68-1.12 8.24-.57 11.34 1.34.37.23.49.71.27 1.08zm.1-2.83c-3.26-1.94-8.65-2.12-11.76-1.18-.5.15-1.02-.13-1.17-.63-.15-.5.13-1.02.63-1.17 3.61-1.1 9.56-.89 13.31 1.34.45.27.6.85.33 1.3-.27.45-.85.6-1.3.34z" />
          </svg>
          <span style={{ fontFamily: "'Cinzel', serif", fontSize: "1.1rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>SPOTIFY</span>
        </div>
        <p style={{ fontSize: "0.75rem", color: "#6b5535", letterSpacing: "0.1em", textTransform: "uppercase" }}>Data Warehouse</p>
      </div>

      <div className="card" style={{ padding: "16px", animation: "slide-in-right 0.5s 0.1s ease forwards", opacity: 0 }}>
        <div style={{ marginBottom: "12px" }}>
          <p style={{ fontSize: "0.85rem", fontWeight: 600, color: "#f0e2bc", marginBottom: "4px" }}>{user?.display_name || "Usuario"}</p>
          <p style={{ fontSize: "0.75rem", color: "#6b5535" }}>{user?.country || "Desconocido"}</p>
        </div>
        <div style={{ height: "1px", background: "var(--border-color)", marginBottom: "12px" }} />
        <div style={{ display: "flex", gap: "12px", fontSize: "0.75rem", color: "#a89060" }}>
          <span>🎵 {user?.product || "Gratis"}</span>
          <span>👥 {user?.followers || 0}</span>
        </div>
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: "8px", flex: 1 }}>
        {menuItems.map((item, i) => {
          const Icon = item.icon;
          const isActive = page === item.id;
          return (
            <button key={item.id} onClick={() => setPage(item.id)} style={{
              background: isActive ? "rgba(201, 168, 76, 0.1)" : "transparent",
              border: `1px solid ${isActive ? "rgba(201, 168, 76, 0.25)" : "transparent"}`,
              color: isActive ? "#f0e2bc" : "#a89060",
              padding: "12px 16px", borderRadius: "4px", cursor: "pointer", display: "flex", alignItems: "center", gap: "12px", fontSize: "0.9rem", transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)", fontWeight: isActive ? 600 : 400, animation: `slide-in-right 0.5s ${0.2 + i * 0.08}s ease forwards`, opacity: 0
            }}
            onMouseEnter={(e) => {
              if (!isActive) { e.currentTarget.style.background = "rgba(201, 168, 76, 0.05)"; e.currentTarget.style.borderColor = "rgba(201, 168, 76, 0.15)"; }
            }}
            onMouseLeave={(e) => {
              if (!isActive) { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "transparent"; }
            }}>
              <Icon size={18} strokeWidth={1.5} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <button onClick={onLogout} style={{
        background: "rgba(180, 50, 50, 0.08)", border: "1px solid rgba(180, 50, 50, 0.2)", color: "#ff9999", padding: "10px 16px", borderRadius: "4px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", fontSize: "0.85rem", transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)", animation: "fade-in-up 0.5s 0.4s ease forwards", opacity: 0
      }}>
        <LogOut size={16} /> Salir
      </button>
    </aside>
  );
}

function TrendIcon({ size = 16, color = "#c9a84c" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  );
}

// ─── DASHBOARD PAGE ──────────────────────────────────────────────────────────
function DashboardPage() {
  const [artists, setArtists] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [stats, setStats] = useState({ total_plays: 0, hourly: [], weekly: [] });
  
  const topArtistCount = useCountUp(stats.total_artists || 0);
  const topTrackCount = useCountUp(stats.total_tracks || 0);
  const totalPlaysCount = useCountUp(stats.total_plays || 0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const topArtistsData = await spotifyApi.getTopArtists();
        setArtists(topArtistsData.slice(0, 5));
        const topTracksData = await spotifyApi.getTopTracks();
        setTracks(topTracksData.slice(0, 5));
        const statsData = await spotifyApi.getStats();
        setStats(statsData);
      } catch (error) {
        console.error("Error cargando dashboard:", error);
      }
    };
    fetchData();
  }, []);

  const isEmpty = stats.total_plays === 0 && artists.length === 0 && tracks.length === 0;

  if (isEmpty) {
    return (
      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px", textAlign: "center", minHeight: "80vh", animation: "fade-in-up 0.6s ease forwards" }}>
        <div style={{
          width: "80px", height: "80px", borderRadius: "50%",
          background: "rgba(201, 168, 76, 0.05)", border: "1px solid rgba(201, 168, 76, 0.2)",
          display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "24px"
        }}>
          <Database size={36} color="var(--gold-main)" strokeWidth={1.5} />
        </div>
        <h2 style={{ fontFamily: "'Cinzel', serif", fontSize: "1.5rem", color: "#f0e2bc", marginBottom: "12px", fontWeight: 400 }}>El Data Warehouse está vacío</h2>
        <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", maxWidth: "450px", lineHeight: 1.6, marginBottom: "32px" }}>
          Tu almacén de datos personales de Spotify se ha inicializado correctamente en PostgreSQL (Neon), pero aún no se ha importado información de escucha.
        </p>
        <button onClick={() => window.location.reload()} className="btn-primary">
          Actualizar Página
        </button>
      </div>
    );
  }

  const chartHourly = Array.from({ length: 24 }, (_, i) => {
    const hourStr = i.toString().padStart(2, '0');
    const existing = stats.hourly.find(h => h.h === hourStr);
    return { h: hourStr, v: existing ? existing.v : 0 };
  });
  const chartWeekly = stats.weekly.length > 0 ? stats.weekly : WEEKLY;

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "32px 40px", animation: "fade-in-up 0.6s ease forwards" }}>
      <div style={{ marginBottom: "40px" }}>
        <h1 className="page-title">Dashboard</h1>
        <p className="subtitle">
          {stats.min_date && stats.max_date 
            ? `Análisis del ${new Date(stats.min_date).toLocaleDateString()} al ${new Date(stats.max_date).toLocaleDateString()}`
            : "Tus hábitos de escucha en un vistazo"}
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px", marginBottom: "40px" }}>
        {[ 
          { label: "Artistas Escuchados", value: topArtistCount, icon: Music }, 
          { label: "Canciones Escuchadas", value: topTrackCount, icon: Star }, 
          { label: "Total Reproducciones", value: totalPlaysCount, icon: TrendingUp },
          { label: "Género Principal", value: stats.genres?.length > 0 ? stats.genres[0].g : "Ninguno", icon: Layers }
        ].map((stat, i) => (
            <div key={stat.label} className="card" style={{ padding: "24px", animation: `fade-in-up 0.5s ${0.1 + i * 0.1}s ease forwards`, opacity: 0 }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
                <div><p style={{ fontSize: "0.75rem", color: "#a89060", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "8px" }}>{stat.label}</p><p className="stat-value">{stat.value}</p></div>
                <stat.icon size={24} color="#c9a84c" strokeWidth={1.5} style={{ opacity: 0.6 }} />
              </div>
            </div>
          ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "24px", marginBottom: "40px" }}>
        {/* Top Artistas */}
        <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.2s ease forwards", opacity: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}><div className="accent-bar" /><h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>ARTISTAS TOP</h3></div>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {artists.length === 0 ? <p style={{color: '#a89060', fontSize: '0.85rem'}}>Cargando artistas...</p> : artists.map((artist, i) => {
              const COLORS = ["#c9a84c", "#e8c467", "#a89060", "#7d6b3d", "#6b5535"];
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: "12px",
                  padding: "8px 12px", borderBottom: "1px solid rgba(201,168,76,.06)",
                  borderRadius: "6px", cursor: "pointer",
                  transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(201, 168, 76, 0.06)";
                  e.currentTarget.style.transform = "translateX(6px)";
                  e.currentTarget.style.paddingLeft = "16px";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "transparent";
                  e.currentTarget.style.transform = "translateX(0)";
                  e.currentTarget.style.paddingLeft = "12px";
                }}
                >
                  <div style={{
                    width: "36px", height: "36px", flexShrink: 0,
                    background: `linear-gradient(135deg, ${COLORS[i % COLORS.length]}, ${COLORS[(i + 1) % COLORS.length]})`,
                    borderRadius: "8px", display: "flex", alignItems: "center",
                    justifyContent: "center", fontWeight: 700, color: "#0a0703", fontSize: "1rem",
                  }}>
                    {i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: ".9rem", color: "#f0e2bc", fontWeight: 600 }}>{artist.name}</p>
                    <p style={{ fontSize: ".7rem", color: "#6b5535" }}>{artist.play_count || 0} reproducciones</p>
                  </div>
                  <TrendIcon size={14} color="#c9a84c" />
                </div>
              );
            })}
          </div>
        </div>

        {/* Canciones Top */}
        <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.25s ease forwards", opacity: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}><div className="accent-bar" /><h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>CANCIONES TOP</h3></div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid rgba(201,168,76,.15)", background: "rgba(201,168,76,.05)" }}>
                {[
                  { label: "Posición", align: "center", width: "10%" },
                  { label: "Canción", align: "left", width: "45%" },
                  { label: "Artista", align: "left", width: "30%" },
                  { label: "Reproducciones", align: "center", width: "15%" }
                ].map((col) => (
                  <th key={col.label} style={{
                    padding: "10px 12px", textAlign: col.align, fontSize: ".7rem",
                    color: "#6b5535", fontWeight: 600, letterSpacing: ".05em", textTransform: "uppercase",
                    width: col.width
                  }}>
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tracks.length === 0 ? (
                <tr><td colSpan="4" style={{ padding: "12px", textAlign: "center", color: "#a89060" }}>Cargando canciones...</td></tr>
              ) : tracks.map((track, i) => (
                <tr key={i} style={{ borderBottom: "1px solid rgba(201, 168, 76, 0.06)" }}>
                  <td style={{ padding: "10px 12px", color: "#c9a84c", fontWeight: 700, textAlign: "center" }}>#{i + 1}</td>
                  <td style={{ padding: "10px 12px", color: "#f0e2bc", fontWeight: 600, textAlign: "left" }}>{track.name}</td>
                  <td style={{ padding: "10px 12px", color: "#a89060", textAlign: "left" }}>{track.artist_name}</td>
                  <td style={{ padding: "10px 12px", color: "#c9a84c", fontWeight: 600, textAlign: "center" }}>{track.play_count || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "40px" }}>
        <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.3s ease forwards", opacity: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "20px" }}><div className="accent-bar" /><h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>ACTIVIDAD POR HORA</h3></div>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={chartHourly}><defs><linearGradient id="colorHourly" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#c9a84c" stopOpacity={0.4} /><stop offset="95%" stopColor="#c9a84c" stopOpacity={0} /></linearGradient></defs><XAxis dataKey="h" stroke="#6b5535" style={{ fontSize: "0.7rem" }} /><YAxis stroke="#6b5535" style={{ fontSize: "0.7rem" }} width={30} /><Tooltip contentStyle={{ background: "rgba(13, 10, 5, 0.95)", border: "1px solid rgba(201, 168, 76, 0.3)", borderRadius: "4px", color: "#f0e2bc" }} /><Area type="monotone" dataKey="v" stroke="#c9a84c" strokeWidth={2} fill="url(#colorHourly)" /></AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.35s ease forwards", opacity: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "20px" }}><div className="accent-bar" /><h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>ACTIVIDAD POR DÍA</h3></div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartWeekly}><XAxis dataKey="d" stroke="#6b5535" style={{ fontSize: "0.7rem" }} /><YAxis stroke="#6b5535" style={{ fontSize: "0.7rem" }} width={30} /><Tooltip contentStyle={{ background: "rgba(13, 10, 5, 0.95)", border: "1px solid rgba(201, 168, 76, 0.3)", borderRadius: "4px", color: "#f0e2bc" }} /><Bar dataKey="v" fill="#c9a84c" radius={[3, 3, 0, 0]} /></BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.4s ease forwards", opacity: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}><div className="accent-bar" /><h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>GÉNEROS FAVORITOS</h3></div>
        <div style={{ width: "100%", height: 320, display: "flex", justifyContent: "center", alignItems: "center" }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={stats.genres?.length > 0 ? stats.genres : GENRES}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ g, v }) => `${g}: ${v}%`}
                outerRadius={100}
                dataKey="v"
              >
                {(stats.genres?.length > 0 ? stats.genres : GENRES).map((_, index) => {
                  const COLORS = ["#c9a84c", "#e8c467", "#a89060", "#7d6b3d", "#6b5535"];
                  return <Cell key={index} fill={COLORS[index % COLORS.length]} />;
                })}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "rgba(10, 7, 3, 0.95)",
                  border: "1px solid #c9a84c",
                  borderRadius: "6px",
                  fontSize: "0.85rem",
                  fontFamily: "'Rajdhani', sans-serif"
                }}
                itemStyle={{ color: "#f0e2bc" }}
                labelStyle={{ display: "none" }}
                formatter={(value, name, props) => [`${value}%`, props.payload.g]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// ─── ETL PAGE ────────────────────────────────────────────────────────────────
function ETLPage() {
  const [status, setStatus] = useState("idle");
  const [history, setHistory] = useState([]);

  const steps = [
    { icon: Database, label: "Extract", desc: "API Spotify" },
    { icon: Layers, label: "Transform", desc: "Normalización" },
    { icon: Zap, label: "Load", desc: "PostgreSQL DWH" },
  ];
  const currentStep = status === "running" ? 1 : status === "done" ? 3 : 0;

  const fetchStatus = async () => {
    try {
      const etlStat = await spotifyApi.getETLStatus();
      setHistory(etlStat);
      // Si la ejecución más reciente sigue RUNNING, marcamos el status local como running
      if (etlStat.length > 0 && etlStat[0].status === "RUNNING") {
        setStatus("running");
      } else if (status === "running") {
        setStatus("done");
      }
    } catch(e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Polling cada 3 segundos si está corriendo
    let interval;
    if (status === "running") {
      interval = setInterval(fetchStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [status]);

  const runETL = async () => {
    if (status === "running") return;
    setStatus("running");
    try {
      await spotifyApi.runETL();
      // El polling en el useEffect se encargará de actualizar el estado
    } catch(e) {
      setStatus("error");
    }
  };

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "32px 40px", animation: "fade-in-up 0.6s ease forwards" }}>
      <div style={{ marginBottom: "40px" }}><h1 className="page-title">Pipeline ETL</h1><p className="subtitle">Orquestación y control de extracción de datos</p></div>
      
      <div className="card" style={{ padding: "40px 32px", marginBottom: "32px", animation: "fade-in-up 0.5s 0.1s ease forwards", opacity: 0 }}>
        <h3 style={{ textAlign: "center", marginBottom: "40px", fontFamily: "'Cinzel', serif", fontSize: "0.9rem", color: "#f0e2bc", letterSpacing: "0.05em" }}>FLUJO DEL PIPELINE</h3>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0", marginBottom: "40px" }}>
          {steps.map((step, i) => {
            const Icon = step.icon;
            const isActive = i < currentStep;
            const isCurrent = status === "running" && i === Math.min(currentStep, 2);

            return (
              <div key={i} style={{ display: "flex", alignItems: "center", flex: 1 }}>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <div style={{
                    width: "48px", height: "48px", borderRadius: "50%",
                    background: isActive ? "rgba(201, 168, 76, 0.1)" : "rgba(201, 168, 76, 0.03)",
                    border: `2px solid ${isActive ? "rgba(201, 168, 76, 0.4)" : "rgba(201, 168, 76, 0.15)"}`,
                    display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "12px", transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  }}>
                    {isCurrent ? <Loader2 size={24} color="#c9a84c" style={{ animation: "rotate-ring 1s linear infinite" }} /> : isActive ? <CheckCircle size={24} color="#c9a84c" /> : <Icon size={24} color={isActive ? "#c9a84c" : "#4a3a20"} strokeWidth={1.5} />}
                  </div>
                  <p style={{ fontFamily: "'Cinzel', serif", fontSize: "0.75rem", fontWeight: 600, color: isActive ? "#c9a84c" : "#4a3a20", letterSpacing: "0.05em", marginBottom: "4px" }}>{step.label}</p>
                  <p style={{ fontSize: "0.7rem", color: "#3a2a10" }}>{step.desc}</p>
                </div>
                {i < 2 && (
                  <div style={{ flex: 1, height: "2px", background: isActive ? "rgba(201, 168, 76, 0.3)" : "rgba(201, 168, 76, 0.1)", margin: "0 16px", marginTop: "-36px", position: "relative" }}>
                    {status === "running" && i === currentStep - 1 && <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "100%", background: "linear-gradient(90deg, transparent, #c9a84c, transparent)", animation: "shimmer 1s ease-in-out infinite" }} />}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <button onClick={runETL} disabled={status === "running"} className="btn-primary" style={{ animation: "fade-in-up 0.5s 0.2s ease forwards", opacity: 0 }}>
            {status === "running" ? <><Loader2 size={16} style={{ animation: "rotate-ring 1s linear infinite" }} /> Procesando...</> : status === "done" ? <><RefreshCw size={16} /> Ejecutar de Nuevo</> : <><Zap size={16} /> Ejecutar Pipeline</>}
          </button>
        </div>
        {status !== "idle" && (
          <div style={{ display: "flex", justifyContent: "center", marginTop: "24px", animation: "scale-in 0.3s ease forwards" }}>
            <div style={{ padding: "8px 20px", borderRadius: "4px", display: "flex", alignItems: "center", gap: "8px", fontSize: "0.75rem", fontFamily: "'Rajdhani', sans-serif", letterSpacing: "0.05em", textTransform: "uppercase", fontWeight: 600 }} className={`status-${status === "done" ? "completed" : status === "error" ? "failed" : "running"}`}>
              {status === "done" ? <CheckCircle size={14} /> : status === "error" ? <XCircle size={14} /> : <Loader2 size={14} style={{ animation: "rotate-ring 1s linear infinite" }} />}
              {status === "running" ? "Pipeline en ejecución" : status === "done" ? "Completado exitosamente" : "Pipeline fallido"}
            </div>
          </div>
        )}
      </div>

      <div className="card" style={{ padding: "28px", animation: "fade-in-up 0.5s 0.2s ease forwards", opacity: 0, overflowX: "auto" }}>
        <h3 style={{ marginBottom: "20px", fontFamily: "'Cinzel', serif", fontSize: "0.9rem", color: "#f0e2bc", letterSpacing: "0.05em" }}>HISTORIAL DE EJECUCIONES</h3>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "600px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)" }}>
              {["Fecha", "Duración", "Artistas", "Tracks", "Historial", "Estado"].map(h => (
                <th key={h} style={{ padding: "12px", textAlign: "left", fontSize: "0.75rem", color: "#6b5535", letterSpacing: "0.1em", textTransform: "uppercase", fontFamily: "'Cinzel', serif", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {history.map((row, i) => (
              <tr key={row.audit_id || i} style={{ borderBottom: "1px solid rgba(201, 168, 76, 0.06)", animation: `fade-in-up 0.4s ${0.3 + i * 0.1}s ease forwards`, opacity: 0, transition: "background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1)" }}
                onMouseEnter={(e) => e.currentTarget.style.background = "rgba(201, 168, 76, 0.03)"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                <td style={{ padding: "12px", fontSize: "0.85rem", color: "#a89060" }}>{new Date(row.started_at).toLocaleString()}</td>
                <td style={{ padding: "12px", fontSize: "0.85rem", color: "#f0e2bc" }}>{row.duration_ms ? (row.duration_ms / 1000).toFixed(1) + "s" : "-"}</td>
                <td style={{ padding: "12px", fontSize: "0.85rem", color: "#c9a84c", fontFamily: "'Cinzel', serif", fontWeight: 600 }}>{row.artists_new}</td>
                <td style={{ padding: "12px", fontSize: "0.85rem", color: "#c9a84c", fontFamily: "'Cinzel', serif", fontWeight: 600 }}>{row.tracks_new}</td>
                <td style={{ padding: "12px", fontSize: "0.85rem", color: "#c9a84c", fontFamily: "'Cinzel', serif", fontWeight: 600 }}>{row.history_new}</td>
                <td style={{ padding: "12px" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "6px", padding: "4px 12px", borderRadius: "3px", fontSize: "0.75rem", letterSpacing: "0.05em", fontFamily: "'Rajdhani', sans-serif", fontWeight: 600, textTransform: "uppercase" }} className={`status-${row.status === "COMPLETED" ? "completed" : "failed"}`}>
                    {row.status === "COMPLETED" ? <CheckCircle size={12} /> : <XCircle size={12} />} {row.status}
                  </span>
                </td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr><td colSpan="6" style={{ padding: "12px", textAlign: "center", color: "#a89060" }}>No hay ejecuciones anteriores.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── PROFILE PAGE ────────────────────────────────────────────────────────────
function ProfilePage({ user }) {
  const userInitial = user?.display_name?.charAt(0)?.toUpperCase() || "U";
  return (
    <div style={{ flex: 1, overflowY: "auto", padding: "32px 40px", animation: "fade-in-up 0.6s ease forwards" }}>
      <div style={{ marginBottom: "40px" }}>
        <h1 className="page-title">Mi Perfil</h1>
        <p className="subtitle">Detalles de tu cuenta de usuario sincronizada</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "32px", alignItems: "start" }}>
        {/* Avatar Card */}
        <div className="card" style={{ padding: "40px 24px", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: "20px" }}>
          <div style={{
            width: "120px", height: "120px", borderRadius: "50%",
            background: "linear-gradient(135deg, rgba(201, 168, 76, 0.15) 0%, rgba(201, 168, 76, 0.02) 100%)",
            border: "2px solid var(--gold-main)", boxShadow: "0 0 20px rgba(201, 168, 76, 0.2)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "3.5rem", fontFamily: "'Cinzel', serif", color: "var(--gold-light)"
          }}>
            {userInitial}
          </div>
          <div>
            <h2 style={{ fontFamily: "'Cinzel', serif", fontSize: "1.2rem", color: "#f0e2bc", marginBottom: "4px" }}>{user?.display_name || "Usuario"}</h2>
            <p style={{ fontSize: "0.8rem", color: "var(--gold-med)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{user?.product || "free"} plan</p>
          </div>
        </div>

        {/* Details Card */}
        <div className="card" style={{ padding: "32px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "24px" }}>
            <div className="accent-bar" />
            <h3 style={{ fontFamily: "'Cinzel', serif", fontSize: "0.9rem", fontWeight: 700, color: "#f0e2bc", letterSpacing: "0.05em" }}>INFORMACIÓN DE LA CUENTA</h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {[
              { label: "ID de Spotify", val: user?.spotify_id },
              { label: "Correo Electrónico", val: user?.email || "No compartido" },
              { label: "País o Región", val: user?.country || "Desconocido" },
              { label: "Seguidores en Spotify", val: user?.followers || 0 },
            ].map((item, idx) => (
              <div key={idx} style={{ borderBottom: "1px solid rgba(201, 168, 76, 0.08)", paddingBottom: "12px" }}>
                <p style={{ fontSize: "0.75rem", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "4px" }}>{item.label}</p>
                <p style={{ fontSize: "0.95rem", color: "#f0e2bc", fontWeight: 500 }}>{item.val}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── APP ROOT ─────────────────────────────────────────────────────────────────
export default function App() {
  const [screen, setScreen] = useState("loading");
  const [page, setPage] = useState("dashboard");
  const [user, setUser] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");
    if (token) {
      localStorage.setItem("spotify_dwh_token", token);
      window.history.replaceState({}, document.title, "/");
      setScreen("callback");
    } else {
      const existingToken = localStorage.getItem("spotify_dwh_token");
      if (existingToken) {
        loadUser();
      } else {
        setScreen("login");
      }
    }
  }, []);

  const loadUser = async () => {
    try {
      const data = await spotifyApi.getProfile();
      setUser(data);
      setScreen("app");
    } catch (e) {
      setScreen("login");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("spotify_dwh_token");
    setScreen("login");
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-0)" }}>
      <style dangerouslySetInnerHTML={{ __html: CSS }} />
      {screen === "loading" && <div />}
      {screen === "login" && <LoginPage />}
      {screen === "callback" && <CallbackPage onDone={loadUser} />}
      {screen === "app" && (
        <div style={{ display: "flex", minHeight: "100vh" }}>
          <Sidebar page={page} setPage={setPage} user={user} onLogout={handleLogout} />
          <main style={{ flex: 1, background: "linear-gradient(135deg, rgba(10, 7, 3, 0.95) 0%, rgba(13, 10, 5, 0.98) 100%)", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", inset: 0, opacity: 0.015, backgroundImage: "linear-gradient(rgba(201, 168, 76, 1) 1px, transparent 1px), linear-gradient(90deg, rgba(201, 168, 76, 1) 1px, transparent 1px)", backgroundSize: "50px 50px", pointerEvents: "none" }} />
            {page === "dashboard" && <DashboardPage />}
            {page === "profile" && <ProfilePage user={user} />}
            {page === "etl" && <ETLPage />}
          </main>
        </div>
      )}
    </div>
  );
}
