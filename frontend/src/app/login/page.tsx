'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Database, Mail, Lock, Loader2, ArrowRight } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import { Button } from '../../components/ui/button';
import ThemeToggle from '../../components/ui/ThemeToggle';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/card';

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
      let mockUid = "regular-user-uuid-87654321";
      let mockRole = "user";

      if (email.includes("admin")) {
        mockUid = "admin-user-uuid-12345678";
        mockRole = "admin";
      }

      const mockToken = `mock-token-${mockRole}-${mockUid}`;

      const profile = await fetch('http://localhost:8000/api/v1/auth/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: mockUid, email, full_name: email.split('@')[0].toUpperCase() })
      }).then(res => {
        if (!res.ok) throw new Error("Backend connection failed. Is the server running?");
        return res.json();
      });

      setSession(profile, mockToken);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || "Failed to establish database session. Ensure FastAPI backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (type: 'admin' | 'user') => {
    setEmail(type === 'admin' ? 'admin@cda.com' : 'user@cda.com');
    setPassword('password');
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center relative px-4 bg-background">
      {/* Top-right controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
        <span className="text-[10px] uppercase tracking-wider text-gray-400 border border-gray-200 dark:border-gray-700 rounded px-2 py-0.5 font-medium">
          Prototype
        </span>
        <ThemeToggle className="h-9 w-9 rounded-md flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer" />
      </div>

      <div className="w-full max-w-md relative z-10">
        <form onSubmit={handleLogin}>
          <Card className="border-border bg-card">
            <CardHeader className="space-y-2 text-center pb-4">
              <div className="flex justify-center mb-1">
                <div className="h-10 w-10 bg-gray-100 dark:bg-gray-800 rounded-md flex items-center justify-center border border-border">
                  <Database className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                </div>
              </div>
              <CardTitle className="text-xl font-bold tracking-tight text-foreground">Conda AI</CardTitle>
              <CardDescription className="text-xs text-muted-foreground">
                Natural language interface to compile PostgreSQL queries
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded-md leading-relaxed">
                  {error}
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@conda.ai"
                    className="w-full bg-background border border-border rounded-md py-2.5 pl-10 pr-4 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-gray-400 transition-colors"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 h-4 w-4 text-muted-foreground" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-background border border-border rounded-md py-2.5 pl-10 pr-4 text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:border-gray-400 transition-colors"
                    required
                  />
                </div>
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4 pt-2">
              <Button type="submit" className="w-full py-2.5" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin text-primary-foreground" /> : 'Sign In'}
              </Button>

              {/* Developer credentials shortcuts */}
              <div className="w-full pt-4 border-t border-border space-y-2">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block text-center">Development Sandbox Shortcuts</span>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleQuickLogin('user')}
                    className="py-2.5 px-3 bg-muted/40 hover:bg-muted border border-border rounded-md text-xs font-medium text-foreground transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>User Sandbox</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickLogin('admin')}
                    className="py-2.5 px-3 bg-muted/40 hover:bg-muted border border-border rounded-md text-xs font-medium text-foreground transition-colors flex items-center justify-between cursor-pointer"
                  >
                    <span>Admin Sandbox</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
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
