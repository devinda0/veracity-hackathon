import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  artifacts?: Artifact[]
  agentTrace?: AgentTrace
  timestamp: Date
  tokensUsed?: number
  cost?: number
}

export interface Artifact {
  id: string
  type: string // "scorecard", "trendmap", "heatmap", etc.
  title: string
  data: Record<string, unknown>
}

export interface AgentTrace {
  agents: AgentStatus[]
  duration_ms: number
}

export interface AgentStatus {
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: Record<string, unknown>
  error?: string
}

interface ChatStore {
  messages: Message[]
  loading: boolean
  error: string | null
  sessionId: string | null
  currentQuery: string

  addMessage: (msg: Message) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  clearMessages: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setSessionId: (id: string) => void
  setCurrentQuery: (query: string) => void
  addArtifact: (messageId: string, artifact: Artifact) => void
  setAgentTrace: (messageId: string, trace: AgentTrace) => void
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
        messages: state.messages.map((m) =>
          m.id === id ? { ...m, ...updates } : m
        ),
      })),

    clearMessages: () => set({ messages: [] }),
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
            : m
        ),
      })),

    setAgentTrace: (messageId, trace) =>
      set((state) => ({
        messages: state.messages.map((m) =>
          m.id === messageId ? { ...m, agentTrace: trace } : m
        ),
      })),
  }))
)

