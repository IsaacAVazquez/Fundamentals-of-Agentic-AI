import { createClient } from '@neondatabase/neon-js';

let cached: { token: string; expiresAt: number } | null = null;

function decodeExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const { exp } = JSON.parse(atob(payload)) as { exp?: number };
    return typeof exp === 'number' ? exp * 1000 : null;
  } catch {
    return null;
  }
}

/**
 * Fetches the signed JWT for the current session from this app's own auth proxy
 * (`/api/auth/token`). The session cookie travels with the request, so the browser
 * never handles a secret. Cached in memory until 30 seconds before it expires.
 */
export async function getToken(): Promise<string | null> {
  if (cached && cached.expiresAt - 30_000 > Date.now()) return cached.token;
  const res = await fetch('/api/auth/token');
  if (!res.ok) {
    cached = null;
    return null;
  }
  const { token } = (await res.json()) as { token?: string };
  if (!token) {
    cached = null;
    return null;
  }
  cached = { token, expiresAt: decodeExpiry(token) ?? Date.now() + 60_000 };
  return token;
}

export function clearToken() {
  cached = null;
}

/**
 * Data API client. Every request carries `Authorization: Bearer <jwt>` and Postgres
 * Row Level Security narrows each query to the signed-in user's rows.
 */
export const db = createClient({
  dataApi: { url: process.env.NEXT_PUBLIC_NEON_DATA_API_URL!, getToken },
});
