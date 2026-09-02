import { auth } from '@/lib/auth/server';

/** Sends visitors without a valid session to the sign-in page before the contacts page renders. */
export default auth.middleware({ loginUrl: '/sign-in' });

export const config = {
  matcher: ['/'],
};
