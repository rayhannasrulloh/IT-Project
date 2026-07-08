'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Sparkles, ShieldCheck, BarChart3, MessagesSquare, Database, Mic,
  ArrowRight, Terminal, Quote, FileText,
} from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import ThemeToggle from '../components/ui/ThemeToggle';

const FEATURES = [
  { icon: ShieldCheck, title: 'Read-only & safe', desc: 'Every query is validated — only SELECT runs. Writes and DDL are blocked by guardrails.' },
  { icon: BarChart3, title: 'Answer, chart & explanation', desc: 'Get the result, an auto-selected chart, and a plain-language summary of what it means.' },
  { icon: MessagesSquare, title: 'Remembers the conversation', desc: 'Ask follow-ups like "only the Gold tier" or "break it down by month" — it keeps context.' },
  { icon: Database, title: 'Grounded in your data', desc: 'Answers come only from your database, with a citation of the source tables — never made up.' },
  { icon: Mic, title: 'Voice to text', desc: 'Speak your question and let the analyst transcribe and run it for you.' },
  { icon: FileText, title: 'Audit & export', desc: 'Every query is logged and filterable; export the report to PDF or CSV in one click.' },
];

const STEPS = [
  { n: '01', title: 'Ask in plain language', desc: '"Who are our top customers by revenue this quarter?"' },
  { n: '02', title: 'Safe SQL, executed', desc: 'A schema-aware, read-only query runs against your database.' },
  { n: '03', title: 'Answer + chart + source', desc: 'You get the number, a chart, an explanation, and where it came from.' },
];

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard');
  }, [isAuthenticated, router]);

  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* ambient glows */}
      <div className="pointer-events-none absolute top-0 left-1/4 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
      <div className="pointer-events-none absolute top-40 right-1/4 h-80 w-80 rounded-full bg-primary/5 blur-3xl" />

      {/* Nav */}
      <nav className="relative max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center shadow-sm">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-sm tracking-tight">Conda AI</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle className="h-9 w-9 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer" />
          <Link href="/login" className="text-xs font-semibold px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors">
            Sign In
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary bg-primary/10 border border-primary/20 rounded-full px-3 py-1">
          <Sparkles className="h-3 w-3" /> Conversational Data Analyst
        </span>
        <h1 className="mt-6 text-4xl sm:text-6xl font-bold tracking-tight leading-[1.05]">
          Chat with your database<br />in plain language
        </h1>
        <p className="mt-6 text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Ask a business question and get a safe SQL query, the answer, a chart, and a plain-language
          explanation — grounded entirely in your data, never invented.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link href="/login" className="inline-flex items-center gap-2 bg-primary text-primary-foreground text-sm font-semibold px-6 py-3 rounded-xl shadow-sm hover:opacity-90 transition-opacity">
            Get Started <ArrowRight className="h-4 w-4" />
          </Link>
          <a href="#how" className="inline-flex items-center gap-2 text-sm font-semibold px-6 py-3 rounded-xl border border-border hover:bg-muted transition-colors">
            See how it works
          </a>
        </div>

        {/* mock chat preview */}
        <div className="mt-14 max-w-2xl mx-auto text-left">
          <div className="rounded-2xl border border-border bg-card shadow-sm p-5 space-y-4">
            <div className="flex justify-end">
              <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm font-medium">
                What is our total revenue?
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-primary to-blue-500 flex items-center justify-center shrink-0">
                <Sparkles className="h-3.5 w-3.5 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-foreground">
                  Your total revenue from paid transactions is <strong>Rp 14,970,759,000</strong>.
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                  <Database className="h-3 w-3" /> Referenced from:
                  <span className="px-1.5 py-0.5 rounded bg-muted/60 border border-border/60 font-mono">payments</span>
                  · live database
                </div>
                <div className="mt-2 inline-flex items-center gap-1.5 text-[11px] text-muted-foreground font-mono bg-[#0f172a] text-blue-300 rounded-lg px-2.5 py-1.5">
                  <Terminal className="h-3 w-3" /> SELECT SUM(amount) FROM payments WHERE status = &apos;paid&apos;;
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">Built for trustworthy self-service analytics</h2>
          <p className="mt-2 text-sm text-muted-foreground">Everyone gets answers in seconds — safely, and grounded in the data.</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-2xl border border-border/70 bg-card p-5 hover:border-border transition-colors">
              <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <f.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="relative max-w-5xl mx-auto px-6 py-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">How it works</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {STEPS.map((s) => (
            <div key={s.n} className="rounded-2xl border border-border/70 bg-card p-6">
              <span className="text-3xl font-bold text-primary/30">{s.n}</span>
              <h3 className="mt-2 text-base font-semibold">{s.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative max-w-4xl mx-auto px-6 py-16">
        <div className="rounded-3xl border border-border bg-card p-10 text-center shadow-sm">
          <Quote className="h-6 w-6 text-primary/40 mx-auto" />
          <h2 className="mt-4 text-2xl sm:text-3xl font-bold tracking-tight">Stop waiting in the analytics queue</h2>
          <p className="mt-3 text-sm text-muted-foreground max-w-xl mx-auto">
            Ask your data anything — no SQL required. Sign in with a sandbox account to try it now.
          </p>
          <Link href="/login" className="mt-6 inline-flex items-center gap-2 bg-primary text-primary-foreground text-sm font-semibold px-6 py-3 rounded-xl shadow-sm hover:opacity-90 transition-opacity">
            Launch Conda AI <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative max-w-6xl mx-auto px-6 py-8 border-t border-border/60 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 bg-primary rounded-md flex items-center justify-center">
            <Sparkles className="h-3 w-3 text-white" />
          </div>
          <span className="font-semibold text-foreground">Conda AI</span>
          <span>· Conversational Data Analyst</span>
        </div>
        <span>Read-only · PostgreSQL · Project 3</span>
      </footer>
    </div>
  );
}
