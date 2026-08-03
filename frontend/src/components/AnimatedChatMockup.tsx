'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowPathIcon, ChartBarIcon } from '@heroicons/react/24/outline';

const FULL_QUESTION = "What is our total revenue?";

const REVENUE_DATA = [
  { month: 'Jan', val: '1.8B', height: '52%' },
  { month: 'Feb', val: '2.2B', height: '64%' },
  { month: 'Mar', val: '2.5B', height: '74%' },
  { month: 'Apr', val: '2.4B', height: '70%' },
  { month: 'May', val: '2.9B', height: '86%' },
  { month: 'Jun', val: '3.1B', height: '98%' },
];

export default function AnimatedChatMockup() {
  const [typedText, setTypedText] = useState('');
  const [step, setStep] = useState<'typing' | 'compiling' | 'result'>('typing');

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (step === 'typing') {
      if (typedText.length < FULL_QUESTION.length) {
        timeoutId = setTimeout(() => {
          setTypedText(FULL_QUESTION.slice(0, typedText.length + 1));
        }, 50);
      } else {
        // Typing finished -> wait briefly then start compiling
        timeoutId = setTimeout(() => {
          setStep('compiling');
        }, 400);
      }
    } else if (step === 'compiling') {
      // Simulate backend compilation time
      timeoutId = setTimeout(() => {
        setStep('result');
      }, 1400);
    } else if (step === 'result') {
      // Hold result state for 6.5s so user can appreciate the chart, then restart loop
      timeoutId = setTimeout(() => {
        setTypedText('');
        setStep('typing');
      }, 6500);
    }

    return () => clearTimeout(timeoutId);
  }, [step, typedText]);

  return (
    <section className="relative max-w-3xl mx-auto px-6 pb-28 z-10">
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="rounded-2xl border border-slate-200/70 dark:border-slate-800/70 bg-white/40 dark:bg-[#151414]/60 backdrop-blur-lg p-5 md:p-6 shadow-xl shadow-slate-200/40 dark:shadow-none space-y-5 min-h-[340px]"
      >
        {/* ── User Query Bubble with Typewriter Effect ── */}
        <div className="flex justify-end min-h-[40px]">
          <div className="bg-[#FF5F08] text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm font-medium shadow-sm flex items-center gap-1">
            <span>{typedText}</span>
            {step === 'typing' && (
              <span className="w-1.5 h-4 bg-white/80 inline-block animate-pulse rounded-xs" />
            )}
          </div>
        </div>

        {/* ── Conda AI Response Area ── */}
        <div className="flex items-start gap-3 min-h-[220px]">
          <div className="h-9 w-9 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
            <Image
              src="/logo/conda-ai.png"
              alt="Conda AI logo"
              width={24}
              height={24}
              className="h-9 w-9 object-contain"
              priority
            />
          </div>

          <div className="flex-1">
            <AnimatePresence mode="wait">
              {step === 'compiling' && (
                <motion.div
                  key="compiling"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.25 }}
                  className="flex items-center space-x-2.5 py-2 px-3.5 border border-slate-200/80 dark:border-slate-800/80 rounded-full w-fit bg-slate-100/60 dark:bg-slate-900/60"
                >
                  <ArrowPathIcon className="h-4 w-4 animate-spin text-[#FF5F08]" />
                  <span className="text-xs text-slate-600 dark:text-[#F0E3DE] font-medium">
                    Analyst compiling SQL query &amp; chart...
                  </span>
                </motion.div>
              )}

              {step === 'result' && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="space-y-3.5"
                >
                  <p className="text-sm text-slate-800 dark:text-[#F0E3DE] leading-relaxed">
                    Your total revenue from paid transactions is <strong className="text-slate-900 dark:text-white font-semibold">Rp 14,970,758,000</strong>.
                  </p>

                  <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-[#F0E3DE]">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-200/60 dark:bg-slate-800/80">
                      Referenced from: payment.csv
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-200/60 dark:bg-slate-800/80">
                      live database
                    </span>
                  </div>

                  {/* ── Animated Mini Bar Chart Data Visualization ── */}
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.15 }}
                    className="bg-slate-100/80 dark:bg-slate-900/10 border border-slate-200/80 dark:border-slate-800/80 rounded-xl p-3.5 space-y-2"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-1.5 font-medium text-slate-700 dark:text-slate-200">
                        <span>Revenue Growth (2024)</span>
                      </div>
                    </div>

                    <div className="h-24 flex items-end justify-between gap-2 pt-3 px-1">
                      {REVENUE_DATA.map((d, idx) => (
                        <div key={d.month} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                          <span className="text-[9px] text-slate-500 dark:text-slate-400 opacity-80 group-hover:opacity-100 transition-opacity">
                            {d.val}
                          </span>
                          <motion.div
                            initial={{ height: 0 }}
                            animate={{ height: d.height }}
                            transition={{ duration: 0.5, delay: 0.2 + idx * 0.08, ease: 'easeOut' }}
                            className="w-full bg-gradient-to-t from-[#FF5F08]/70 to-[#FF5F08] rounded-t-sm relative shadow-xs group-hover:brightness-110 transition-all"
                          />
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                            {d.month}
                          </span>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* ── SQL Query Snippet ── */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.3 }}
                    className="bg-slate-200/60 dark:bg-[#151414]/90 text-left p-3.5 rounded-lg font-mono text-[11px] text-slate-800 dark:text-[#F0E3DE] overflow-x-auto whitespace-nowrap border border-slate-300/40 dark:border-slate-800/60 shadow-xs"
                  >
                    <span className="text-[#FF5F08] font-bold select-none">&gt; </span>
                    <span>SELECT SUM(amount) FROM payments WHERE status = &apos;paid&apos;;</span>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
