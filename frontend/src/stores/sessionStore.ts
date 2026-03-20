import { create } from 'zustand';

import { apiFetch } from '@/utils/api';
import { useChatStore, type Message } from '@/stores/chatStore';

interface SessionApiResponse {
  id: string;
  title: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface SessionDetailApiResponse extends SessionApiResponse {
  messages: MessageApiResponse[];
}

interface MessageApiResponse {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  artifacts?: Message['artifacts'];
  agent_trace?: Message['agentTrace'];
  timestamp: string;
  tokens_used?: number;
  cost?: number;
}

interface SessionListApiResponse {
  sessions: SessionApiResponse[];
  total: number;
}

export interface Session {
  id: string;
  title: string;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

interface SessionStore {
  activeSessionId: string | null;
  error: string | null;
  loading: boolean;
  sessions: Session[];
  createSession: () => Promise<void>;
  deleteSession: (id: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  renameSession: (id: string, title: string) => Promise<void>;
  selectSession: (id: string) => Promise<void>;
  bumpMessageCount: (sessionId: string, by?: number) => void;
}

function toSession(session: SessionApiResponse): Session {
  return {
    id: session.id,
    title: session.title,
    description: session.description ?? undefined,
    createdAt: new Date(session.created_at),
    updatedAt: new Date(session.updated_at),
    messageCount: session.message_count,
  };
}

function toMessage(message: MessageApiResponse): Message {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    artifacts: message.artifacts,
    agentTrace: message.agent_trace,
    timestamp: new Date(message.timestamp),
    tokensUsed: message.tokens_used,
    cost: message.cost,
  };
}

export const useSessionStore = create<SessionStore>((set, get) => ({
  activeSessionId: null,
  error: null,
  loading: false,
  sessions: [],
  bumpMessageCount: (sessionId, by = 2) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === sessionId ? { ...s, messageCount: s.messageCount + by } : s,
      ),
    })),
  createSession: async () => {
    set({ loading: true, error: null });

    try {
      const created = await apiFetch<SessionApiResponse>('/api/v1/sessions', {
        method: 'POST',
        body: JSON.stringify({
          title: `Research thread ${new Date().toLocaleDateString()}`,
          description: '',
        }),
      });
      const session = toSession(created);

      set((state) => ({
        activeSessionId: session.id,
        loading: false,
        sessions: [session, ...state.sessions],
      }));

      useChatStore.getState().setCurrentQuery('');
      useChatStore.getState().setMessages([]);
      useChatStore.getState().setSessionId(session.id);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create session',
        loading: false,
      });
    }
  },
  deleteSession: async (id) => {
    set({ loading: true, error: null });

    try {
      await apiFetch<void>(`/api/v1/sessions/${id}`, { method: 'DELETE' });

      const remaining = get().sessions.filter((session) => session.id !== id);
      const isActive = get().activeSessionId === id;

      set({
        activeSessionId: isActive ? null : get().activeSessionId,
        loading: false,
        sessions: remaining,
      });

      if (!isActive) {
        return;
      }

      const nextSession = remaining[0];
      if (nextSession) {
        await get().selectSession(nextSession.id);
        return;
      }

      useChatStore.getState().setCurrentQuery('');
      useChatStore.getState().setMessages([]);
      useChatStore.getState().setSessionId(null);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete session',
        loading: false,
      });
    }
  },
  loadSessions: async () => {
    set({ loading: true, error: null });

    try {
      const response = await apiFetch<SessionListApiResponse>('/api/v1/sessions');
      const sessions = response.sessions.map(toSession);

      set((state) => ({
        activeSessionId:
          state.activeSessionId && sessions.some((session) => session.id === state.activeSessionId)
            ? state.activeSessionId
            : (sessions[0]?.id ?? null),
        loading: false,
        sessions,
      }));

      const nextSessionId = get().activeSessionId;
      if (nextSessionId) {
        await get().selectSession(nextSessionId);
        return;
      }

      useChatStore.getState().setMessages([]);
      useChatStore.getState().setSessionId(null);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to load sessions',
        loading: false,
      });
    }
  },
  renameSession: async (id, title) => {
    set({ loading: true, error: null });

    try {
      const updated = await apiFetch<SessionApiResponse>(`/api/v1/sessions/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ title }),
      });
      const session = toSession(updated);

      set((state) => ({
        loading: false,
        sessions: state.sessions.map((entry) => (entry.id === id ? session : entry)),
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to rename session',
        loading: false,
      });
    }
  },
  selectSession: async (id) => {
    set({ activeSessionId: id, loading: true, error: null });

    try {
      const detail = await apiFetch<SessionDetailApiResponse>(`/api/v1/sessions/${id}`);
      const session = toSession(detail);

      set((state) => ({
        activeSessionId: session.id,
        loading: false,
        sessions: state.sessions.map((entry) => (entry.id === session.id ? session : entry)),
      }));

      useChatStore.getState().setCurrentQuery('');
      useChatStore.getState().setMessages(detail.messages.map(toMessage));
      useChatStore.getState().setSessionId(session.id);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to open session',
        loading: false,
      });
    }
  },
}));
