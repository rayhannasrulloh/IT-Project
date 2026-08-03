'use client';

import React from 'react';
import { motion } from 'motion/react';
import { ShieldCheckIcon, ChartBarIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

export interface GridItem {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  desc: string;
}

interface CornerAccentGridProps {
  items?: GridItem[];
  className?: string;
}

const DEFAULT_ITEMS: GridItem[] = [
  {
    icon: ShieldCheckIcon,
    title: 'Read-only & safe',
    desc: 'Every query is validated, only SELECT runs. Writes and DDL are blocked by guardrails.',
  },
  {
    icon: ChartBarIcon,
    title: 'Answer, chart & explanation',
    desc: 'Get the result, an auto-selected chart, and a plain-language summary of what it means.',
  },
  {
    icon: ChatBubbleLeftRightIcon,
    title: 'Remembers conversation',
    desc: 'Ask follow-up questions and context is maintained throughout your analytical session.',
  },
];

export default function CornerAccentGrid({ items, className = '' }: CornerAccentGridProps) {
  const gridItems = items || DEFAULT_ITEMS;

  return (
    <div className={`relative border border-slate-200/80 dark:border-[rgba(240,227,222,0.125)] bg-[#FAFAFA] dark:bg-[#151414] ${className}`}>
      {/* ── Outer Corner Accent Squares ── */}
      <span className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-[#FAFAFA] dark:bg-[#151414] border border-slate-400 dark:border-neutral-600 z-10 pointer-events-none" />
      <span className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-[#FAFAFA] dark:bg-[#151414] border border-slate-400 dark:border-neutral-600 z-10 pointer-events-none" />
      <span className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-[#FAFAFA] dark:bg-[#151414] border border-slate-400 dark:border-neutral-600 z-10 pointer-events-none" />
      <span className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-[#FAFAFA] dark:bg-[#151414] border border-slate-400 dark:border-neutral-600 z-10 pointer-events-none" />

      {/* ── 3-Column Grid Container with Dividers ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-200/80 dark:divide-[rgba(240,227,222,0.125)]">
        {gridItems.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ duration: 0.4, delay: i * 0.05 }}
            className="p-6 md:p-8 transition-all duration-300 relative group"
          >
            <f.icon className="h-7 w-7 shrink-0 text-[#FF5F08] dark:text-[#F0E3DE] mb-3" />
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">{f.title}</h3>
            <p className="text-sm text-slate-500 dark:text-[#F0E3DE] leading-relaxed">{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
