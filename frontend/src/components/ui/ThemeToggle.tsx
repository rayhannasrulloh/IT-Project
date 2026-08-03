'use client';

import React, { useEffect, useState } from 'react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

/**
 * Toggles the `dark` class on <html> and persists the choice to localStorage.
 * The initial class is set by the inline script in layout.tsx (no flash).
 */
export const ThemeToggle: React.FC<{ className?: string }> = ({ className }) => {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggle = () => {
    const next = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', next);
    try {
      localStorage.setItem('theme', next ? 'dark' : 'light');
    } catch {
      /* ignore */
    }
    setIsDark(next);
  };

  return (
    <button
      onClick={toggle}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`group hover:scale-105 active:scale-95 ${
        className ??
        'h-10 w-10 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-card hover:text-foreground cursor-pointer'
      }`}
    >
      {isDark ? (
        <SunIcon className="h-5 w-5 group-hover:rotate-90" />
      ) : (
        <MoonIcon className="h-5 w-5 group-hover:-rotate-12" />
      )}
    </button>
  );
};

export default ThemeToggle;
