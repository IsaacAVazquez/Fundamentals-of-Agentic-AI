'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authClient, runAuth } from '@/lib/auth/client';

/** Small caps field labels, shared with the contact form. */
export const labelClassName = 'font-condensed text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground';

export function AuthForm({ mode }: { mode: 'sign-in' | 'sign-up' }) {
  const router = useRouter();
  const signIn = mode === 'sign-in';
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get('email') ?? '');
    const password = String(form.get('password') ?? '');
    const name = String(form.get('name') ?? '');

    setPending(true);
    setError(null);
    const message = await runAuth(() =>
      signIn ? authClient.signIn.email({ email, password }) : authClient.signUp.email({ name, email, password }),
    );
    setPending(false);
    if (message) {
      setError(message);
      return;
    }
    router.push('/');
    router.refresh();
  }

  // The cover of the directory: blue cloth, gold stamping, and the sign-in form set as the bookplate.
  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-cover px-4 py-12 text-cover-foreground">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="font-condensed text-4xl font-bold uppercase leading-none tracking-[0.08em] text-gold text-balance">
            Networking Tracker
          </h1>
          <p className="mx-auto mt-3 max-w-xs text-sm leading-relaxed text-cover-foreground/85 text-pretty">
            A private list of the people you want to stay connected with at Berkeley.
          </p>
        </div>

        <div className="bg-background p-1.5 text-foreground shadow-[0_16px_40px_-16px_rgba(0,0,0,0.6)]">
          <div className="border border-gold px-5 py-6 sm:px-6">
            <h2 className="font-condensed text-xl font-bold uppercase leading-none tracking-[0.1em]">
              {signIn ? 'Sign in' : 'Create your account'}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {signIn ? 'Your contacts are private to your account.' : 'Passwords need at least 8 characters.'}
            </p>
            <form onSubmit={onSubmit} noValidate={false} className="mt-6 grid gap-4">
              {!signIn && (
                <div className="grid gap-1.5">
                  <Label htmlFor="name" className={labelClassName}>
                    Name
                  </Label>
                  <Input id="name" name="name" required autoComplete="name" />
                </div>
              )}
              <div className="grid gap-1.5">
                <Label htmlFor="email" className={labelClassName}>
                  Email
                </Label>
                <Input id="email" name="email" type="email" required autoComplete="email" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="password" className={labelClassName}>
                  Password
                </Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  required
                  minLength={8}
                  autoComplete={signIn ? 'current-password' : 'new-password'}
                />
              </div>
              {error && (
                <p role="alert" className="text-sm text-destructive">
                  {error}
                </p>
              )}
              <Button type="submit" size="lg" className="mt-1 w-full font-condensed text-base font-semibold uppercase tracking-[0.1em]" disabled={pending}>
                {pending ? 'Please wait' : signIn ? 'Sign in' : 'Create account'}
              </Button>
              <p className="text-sm text-muted-foreground">
                {signIn ? (
                  <>
                    New here?{' '}
                    <Link className="font-medium text-primary underline" href="/sign-up">
                      Create an account
                    </Link>
                  </>
                ) : (
                  <>
                    Already have an account?{' '}
                    <Link className="font-medium text-primary underline" href="/sign-in">
                      Sign in
                    </Link>
                  </>
                )}
              </p>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}
