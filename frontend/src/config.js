/**
 * Centralized API configuration.
 *
 * In development:  set VITE_API_URL in frontend/.env (defaults to localhost)
 * In production:   set VITE_API_URL=https://your-api-domain.com
 *
 * NEVER hardcode the API URL directly in service or component files.
 */
export const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
