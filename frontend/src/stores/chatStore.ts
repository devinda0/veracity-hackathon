import { create } from 'zustand';

import type { Message } from '@/types';

interface ChatStore {
  draft: string;
  isStreaming: boolean;
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setDraft: (draft: string) => void;
  setStreaming: (value: boolean) => void;
}

const initialMessages: Message[] = [
  {
    id: 'assistant-bootstrap',
    role: 'assistant',
    content:
      'Workspace initialized. Ask for a market brief, pricing teardown, or competitor snapshot to exercise the shell.',
    timestamp: new Date().toISOString(),
  },
];

export const useChatStore = create<ChatStore>((set) => ({
  draft: '',
  isStreaming: false,
  messages: initialMessages,
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () => set({ messages: [] }),
  setDraft: (draft) => set({ draft }),
  setStreaming: (value) => set({ isStreaming: value }),
}));

