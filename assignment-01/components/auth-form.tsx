'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authClient, runAuth } from '@/lib/auth/client';

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

  return (
    <main className="flex flex-1 items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{signIn ? 'Sign in' : 'Create your account'}</CardTitle>
          <CardDescription>
            {signIn ? 'Your contacts are private to your account.' : 'Passwords need at least 8 characters.'}
          </CardDescription>
        </CardHeader>
        <form onSubmit={onSubmit} noValidate={false}>
          <CardContent className="grid gap-4">
            {!signIn && (
              <div className="grid gap-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" name="name" required autoComplete="name" />
              </div>
            )}
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" required autoComplete="email" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
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
          </CardContent>
          <CardFooter className="mt-6 flex flex-col gap-3">
            <Button type="submit" className="w-full" disabled={pending}>
              {pending ? 'Please wait' : signIn ? 'Sign in' : 'Create account'}
            </Button>
            <p className="text-sm text-muted-foreground">
              {signIn ? (
                <>
                  New here?{' '}
                  <Link className="underline" href="/sign-up">
                    Create an account
                  </Link>
                </>
              ) : (
                <>
                  Already have an account?{' '}
                  <Link className="underline" href="/sign-in">
                    Sign in
                  </Link>
                </>
              )}
            </p>
          </CardFooter>
        </form>
      </Card>
    </main>
  );
}
