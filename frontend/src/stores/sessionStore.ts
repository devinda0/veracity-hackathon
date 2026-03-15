import { create } from 'zustand';

import type { SessionSummary } from '@/types';

interface SessionStore {
  activeSessionId: string | null;
  sessions: SessionSummary[];
  createSession: () => void;
  ensureSeedData: () => void;
  selectSession: (id: string) => void;
}

const seedSessions: SessionSummary[] = [
  {
    id: 'session-ai-db',
    title: 'Vector DB market scan',
    summary: 'Signals across pricing, distribution, and developer adoption.',
    status: 'active',
  },
  {
    id: 'session-win-loss',
    title: 'Win/loss review',
    summary: 'Placeholder thread for enterprise evaluation feedback.',
    status: 'draft',
  },
];

export const useSessionStore = create<SessionStore>((set, get) => ({
  activeSessionId: seedSessions[0]?.id ?? null,
  sessions: seedSessions,
  createSession: () =>
    set((state) => {
      const id = `session-${crypto.randomUUID()}`;
      const session: SessionSummary = {
        id,
        title: 'New research thread',
        summary: 'Fresh session scaffold awaiting backend persistence.',
        status: 'draft',
      };

      return {
        activeSessionId: id,
        sessions: [session, ...state.sessions],
      };
    }),
  ensureSeedData: () => {
    if (get().sessions.length > 0) {
      return;
    }

    set({
      activeSessionId: seedSessions[0]?.id ?? null,
      sessions: seedSessions,
    });
  },
  selectSession: (id) => set({ activeSessionId: id }),
}));

