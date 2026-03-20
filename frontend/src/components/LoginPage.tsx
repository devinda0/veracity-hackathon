import { type FormEvent, useState } from 'react';

import { useAuthStore } from '@/stores/authStore';

type Tab = 'login' | 'register';

export function LoginPage() {
  const [tab, setTab] = useState<Tab>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const { login, register, loading } = useAuthStore();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLocalError(null);

    try {
      if (tab === 'login') {
        await login(email.trim(), password);
      } else {
        if (!name.trim()) {
          setLocalError('Name is required');
          return;
        }
        await register(name.trim(), email.trim(), password);
      }
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Something went wrong');
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      {/* Background gradients */}
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,107,53,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(24,78,67,0.16),_transparent_38%)]" />
      <div className="pointer-events-none fixed inset-0 bg-grid-fade bg-[size:28px_28px] opacity-40" />

      <div className="relative w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <p className="font-display text-4xl tracking-tight text-ink">CoALA</p>
          <p className="mt-2 text-sm text-ink/60">
            Research orchestration workspace
          </p>
        </div>

        {/* Card */}
        <div className="panel-surface p-8">
          {/* Tabs */}
          <div className="mb-6 flex rounded-2xl border border-ink/10 bg-sand/60 p-1">
            {(['login', 'register'] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => { setTab(t); setLocalError(null); }}
                className={`flex flex-1 items-center justify-center rounded-xl py-2 text-sm font-semibold capitalize transition ${
                  tab === t ? 'bg-ink text-canvas shadow-sm' : 'text-ink/55 hover:text-ink'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <form onSubmit={(e) => { void handleSubmit(e); }} className="flex flex-col gap-4">
            {tab === 'register' && (
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold uppercase tracking-widest text-ink/50">
                  Name
                </label>
                <input
                  type="text"
                  autoComplete="name"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full rounded-2xl border border-ink/15 bg-white/80 px-4 py-3 text-sm text-ink placeholder-ink/30 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20"
                />
              </div>
            )}

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-widest text-ink/50">
                Email
              </label>
              <input
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-2xl border border-ink/15 bg-white/80 px-4 py-3 text-sm text-ink placeholder-ink/30 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-widest text-ink/50">
                Password
              </label>
              <input
                type="password"
                autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full rounded-2xl border border-ink/15 bg-white/80 px-4 py-3 text-sm text-ink placeholder-ink/30 outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </div>

            {localError && (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {localError}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-2 w-full rounded-full bg-accent py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-accent/90 disabled:opacity-60"
            >
              {loading ? 'Please wait…' : tab === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-ink/40">
            {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={() => { setTab(tab === 'login' ? 'register' : 'login'); setLocalError(null); }}
              className="font-semibold text-accent underline-offset-2 hover:underline"
            >
              {tab === 'login' ? 'Register' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
