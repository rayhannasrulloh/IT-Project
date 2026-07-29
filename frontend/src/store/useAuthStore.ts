import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Profile } from '../types';

interface AuthState {
  user: Profile | null;
  token?: string | null;
  isAuthenticated: boolean;
  // Whether the persisted store has finished loading from localStorage yet.
  // Route guards must wait for this before deciding to redirect, otherwise a
  // hard refresh briefly sees isAuthenticated=false and bounces to /login.
  hasHydrated: boolean;
  setSession: (user: Profile, token?: string | null) => void;
  clearSession: () => void;
  setHasHydrated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      hasHydrated: false,
      setSession: (user, token = null) => set({ user, token, isAuthenticated: true }),
      clearSession: () => set({ user: null, token: null, isAuthenticated: false }),
      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: 'cda-auth-store', // persisted inside localStorage
      // Only persist the session — never the transient hydration flag.
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      // Fires once rehydration from localStorage completes.
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
