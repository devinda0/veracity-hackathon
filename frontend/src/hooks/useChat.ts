import { startTransition } from 'react';

import { useChatStore } from '@/stores/chatStore';

export function useChat() {
  const messages = useChatStore((state) => state.messages);
  const draft = useChatStore((state) => state.draft);
  const isStreaming = useChatStore((state) => state.isStreaming);
  const addMessage = useChatStore((state) => state.addMessage);
  const setDraftState = useChatStore((state) => state.setDraft);
  const setStreaming = useChatStore((state) => state.setStreaming);

  const setDraft = (value: string) => {
    startTransition(() => {
      setDraftState(value);
    });
  };

  const submitDraft = async () => {
    const content = draft.trim();

    if (!content) {
      return;
    }

    const timestamp = new Date().toISOString();

    addMessage({
      id: `user-${timestamp}`,
      role: 'user',
      content,
      timestamp,
    });
    setDraftState('');
    setStreaming(true);

    await new Promise((resolve) => window.setTimeout(resolve, 350));

    addMessage({
      id: `assistant-${timestamp}`,
      role: 'assistant',
      content:
        'Frontend scaffold is live. API integration, streaming, and artifact hydration will connect in later milestones.',
      timestamp: new Date().toISOString(),
      artifacts: [
        {
          id: `artifact-${timestamp}`,
          kind: 'scorecard',
          title: 'Scaffold coverage',
          rows: [
            { label: 'Vite + React 18', value: 'ready', confidence: 'high' },
            { label: 'Tailwind + PostCSS', value: 'ready', confidence: 'high' },
            { label: 'Zustand stores', value: 'ready', confidence: 'high' },
          ],
        },
      ],
    });

    setStreaming(false);
  };

  return {
    draft,
    isStreaming,
    messages,
    setDraft,
    submitDraft,
  };
}

