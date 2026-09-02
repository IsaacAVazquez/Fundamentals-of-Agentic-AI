'use client';

import { createAuthClient } from '@neondatabase/neon-js/auth/next';

/** Browser auth client. It talks to this app's /api/auth proxy, never to Neon directly. */
export const authClient = createAuthClient();

/** Runs an auth call and returns an error message, or null on success. */
export async function runAuth(
  action: () => Promise<{ error?: { message?: string } | null } | undefined>,
): Promise<string | null> {
  try {
    const result = await action();
    return result?.error ? result.error.message || 'Something went wrong. Try again.' : null;
  } catch (error) {
    return error instanceof Error ? error.message : 'Something went wrong. Try again.';
  }
}
