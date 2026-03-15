import { startTransition } from 'react';

import { useChatStore } from '@/stores/chatStore';

export function useChat() {
  const messages = useChatStore((state) => state.messages);
  const currentQuery = useChatStore((state) => state.currentQuery);
  const loading = useChatStore((state) => state.loading);
  const sessionId = useChatStore((state) => state.sessionId);
  const addMessage = useChatStore((state) => state.addMessage);
  const setCurrentQueryState = useChatStore((state) => state.setCurrentQuery);
  const setLoading = useChatStore((state) => state.setLoading);

  const setCurrentQuery = (value: string) => {
    startTransition(() => {
      setCurrentQueryState(value);
    });
  };

  const submitDraft = async () => {
    const content = currentQuery.trim();

    if (!content) {
      return;
    }

    const now = new Date();
    const ts = now.toISOString();

    addMessage({
      id: `user-${ts}`,
      role: 'user',
      content,
      timestamp: now,
    });
    setCurrentQueryState('');
    setLoading(true);

    await new Promise((resolve) => window.setTimeout(resolve, 350));

    addMessage({
      id: `assistant-${ts}`,
      role: 'assistant',
      content:
        'Frontend scaffold is live. API integration, streaming, and artifact hydration will connect in later milestones.',
      timestamp: new Date(),
      artifacts: [
        {
          id: `artifact-${ts}`,
          type: 'scorecard',
          title: 'Scaffold coverage',
          data: {
            rows: [
              { label: 'Vite + React 18', value: 'ready', confidence: 'high' },
              { label: 'Tailwind + PostCSS', value: 'ready', confidence: 'high' },
              { label: 'Zustand stores', value: 'ready', confidence: 'high' },
            ],
          },
        },
      ],
    });

    setLoading(false);
  };

  return {
    currentQuery,
    loading,
    messages,
    sessionId,
    setCurrentQuery,
    submitDraft,
  };
}
