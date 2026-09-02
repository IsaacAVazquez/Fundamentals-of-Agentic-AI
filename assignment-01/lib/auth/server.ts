import { createNeonAuth } from '@neondatabase/neon-js/auth/next/server';

/**
 * Server-side Neon Auth instance. It proxies /api/auth/* to Neon's managed Better Auth
 * service and keeps the session in a first-party, HttpOnly cookie signed with the
 * server-only cookie secret.
 */
export const auth = createNeonAuth({
  baseUrl: process.env.NEXT_PUBLIC_NEON_AUTH_URL!,
  cookies: { secret: process.env.NEON_AUTH_COOKIE_SECRET! },
});
