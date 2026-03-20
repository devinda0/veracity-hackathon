import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  artifacts?: Artifact[];
  agentTrace?: AgentTrace;
  timestamp: Date;
  tokensUsed?: number;
  cost?: number;
}

export interface Artifact {
  id: string;
  type: string;
  title: string;
  data: Record<string, unknown>;
}

export interface AgentTrace {
  agents: AgentStatus[];
  duration_ms: number;
}

export interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration_ms?: number;
  result?: Record<string, unknown>;
  error?: string;
}

export interface ClarificationOption {
  id: string;
  text: string;
  query: string;
}

interface ChatStore {
  messages: Message[];
  loading: boolean;
  error: string | null;
  sessionId: string | null;
  currentQuery: string;
  liveAgentStatuses: AgentStatus[];
  clarificationOptions: ClarificationOption[] | null;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSessionId: (id: string | null) => void;
  setCurrentQuery: (query: string) => void;
  addArtifact: (messageId: string, artifact: Artifact) => void;
  setAgentTrace: (messageId: string, trace: AgentTrace) => void;
  setLiveAgentStatus: (name: string, status: AgentStatus['status'], durationMs?: number, error?: string) => void;
  clearLiveAgentStatuses: () => void;
  setClarificationOptions: (opts: ClarificationOption[] | null) => void;
}

export const useChatStore = create<ChatStore>()(
  devtools((set) => ({
    messages: [],
    loading: false,
    error: null,
    sessionId: null,
    currentQuery: '',

    addMessage: (msg) =>
      set((state) => ({
        messages: [...state.messages, msg],
      })),

    updateMessage: (id, updates) =>
      set((state) => ({
        messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
      })),

    clearMessages: () => set({ messages: [] }),
    setMessages: (messages) => set({ messages }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    setSessionId: (id) => set({ sessionId: id }),
    setCurrentQuery: (query) => set({ currentQuery: query }),

    addArtifact: (messageId, artifact) =>
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === messageId
            ? {
                ...m,
                artifacts: [...(m.artifacts || []), artifact],
              }
            : m,
        ),
      })),

    setAgentTrace: (messageId, trace) =>
      set((state) => ({
        messages: state.messages.map((m) => (m.id === messageId ? { ...m, agentTrace: trace } : m)),
      })),

    liveAgentStatuses: [],
    clearLiveAgentStatuses: () => set({ liveAgentStatuses: [] }),
    setLiveAgentStatus: (name, status, durationMs, error) =>
      set((state) => {
        const existing = state.liveAgentStatuses.find((a) => a.name === name);
        if (existing) {
          return {
            liveAgentStatuses: state.liveAgentStatuses.map((a) =>
              a.name === name ? { ...a, status, duration_ms: durationMs, error } : a,
            ),
          };
        }
        return {
          liveAgentStatuses: [...state.liveAgentStatuses, { name, status, duration_ms: durationMs, error }],
        };
      }),

    clarificationOptions: null,
    setClarificationOptions: (opts) => set({ clarificationOptions: opts }),
  })),
);
