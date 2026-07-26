'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { SparklesIcon, EnvelopeIcon, LockClosedIcon, ArrowPathIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { useAuthStore } from '../../store/useAuthStore';
import { Button } from '../../components/ui/button';
import ThemeToggle from '../../components/ui/ThemeToggle';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';
import { api } from '../../services/api';
import { supabase } from '../../lib/supabase';

export default function LoginPage() {
  const router = useRouter();
  const { setSession } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setError(null);

    try {
      // Step 1: Authenticate with real Supabase Auth SDK
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError || !data.session) {
        throw new Error(authError?.message || 'Authentication failed. Invalid email or password.');
      }

      const session = data.session;
      const user = data.user;

      // Step 2: Synchronize Supabase user profile with our PostgreSQL backend using the real Supabase JWT token
      const profile = await api.syncProfile(
        user.id,
        user.email || email,
        user.user_metadata?.full_name || email.split('@')[0].toUpperCase(),
        session.access_token
      );

      // Step 3: Persist verified profile and token in store
      setSession(profile, profile.token || session.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (type: 'admin' | 'user') => {
    setEmail(type === 'admin' ? 'admin@cda.com' : 'user@cda.com');
    setPassword('password');
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative overflow-hidden px-4">
      {/* Background soft ambient glows */}
      <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-indigo-500/5 blur-3xl" />

      <ThemeToggle className="absolute top-4 right-4 z-20 h-9 w-9 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer" />
      
      <div className="w-full max-w-md relative z-10">
        <form onSubmit={handleLogin}>
          <Card className="border-border/60 bg-white/40 dark:bg-[#000] backdrop-blur-lg shadow-xl">
            <CardHeader className="space-y-2 text-center pb-4">
              <div className="flex justify-center mb-4">
                <img src="/logo/CondaAI.png" alt="Conda AI logo" className="h-8 w-8 rounded-xl shadow-sm dark:invert dark:brightness-200" />
              </div>
              <CardTitle className="text-xl font-bold tracking-tight text-foreground">Conda AI</CardTitle>
              <CardDescription className="text-xs text-muted-foreground">
                Natural language interface to compile SQL queries
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 bg-danger/10 border border-danger/25 text-danger text-xs rounded-lg leading-relaxed">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Email Address</label>
                <div className="relative">
                  <EnvelopeIcon className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@conda.ai"
                    className="w-full bg-background border border-border/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:bg-muted/20 transition-colors"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Password</label>
                <div className="relative">
                  <LockClosedIcon className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-background border border-border/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary focus:bg-muted/20 transition-colors"
                    required
                  />
                </div>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4 pt-2">
              <Button type="submit" className="w-full py-2.5" disabled={loading}>
                {loading ? <ArrowPathIcon className="h-4 w-4 animate-spin text-primary-foreground" /> : 'Sign In'}
              </Button>

              <div className="text-center text-xs text-muted-foreground">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="text-primary hover:text-primary/80 font-semibold transition-colors">
                  Register
                </Link>
              </div>

              {/* Developer credentials shortcuts */}
              <div className="w-full pt-4 border-t border-border space-y-2">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block text-center">Development Sandbox Shortcuts</span>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleQuickLogin('user')}
                    className="py-2.5 px-3 bg-blue-100/10 hover:bg-blue-200/20 border border-border/60 rounded-xl text-xs font-medium text-foreground transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>User Sandbox</span>
                    <ArrowRightIcon className="h-3 w-3 text-muted-foreground" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickLogin('admin')}
                    className="py-2.5 px-3 bg-blue-100/10 hover:bg-blue-200/20 border border-border/60 rounded-xl text-xs font-medium text-foreground transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>Admin Sandbox</span>
                    <ArrowRightIcon className="h-3 w-3 text-muted-foreground" />
                  </button>
                </div>
              </div>
            </CardFooter>
          </Card>
        </form>
      </div>
    </div>
  );
}
