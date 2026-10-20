// Centralized ShelfLife API Configuration
// When served via Vite dev server (port 5173 or other local port),
// all API traffic routes through the '/api' Vite proxy to prevent CORS and VPN routing issues.

export const API_BASE =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" &&
   (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") &&
   window.location.port !== "8000"
    ? "/api"
    : "http://127.0.0.1:8000");

export default API_BASE;
