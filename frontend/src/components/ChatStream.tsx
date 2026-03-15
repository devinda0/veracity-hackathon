import { useEffect, useRef } from 'react';

import { MessageBubble } from '@/components/MessageBubble';
import { useChatStore } from '@/stores/chatStore';

export function ChatStream() {
  const messages = useChatStore((state) => state.messages);
  const loading = useChatStore((state) => state.loading);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto bg-gradient-to-b from-gray-50 to-white p-4 md:p-6">
      <div className="mx-auto w-full max-w-3xl space-y-4">
        {messages.length === 0 ? (
          <div className="py-12 text-center text-gray-400">
            <div className="mb-4 text-4xl">💡</div>
            <p>Start a conversation about your market and growth strategy</p>
          </div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}

        {loading && (
          <div className="flex gap-3 rounded-lg bg-gray-100 p-4">
            <div className="h-8 w-8 animate-pulse rounded-full bg-gradient-to-r from-blue-400 to-blue-600" />
            <div className="flex-1">
              <div className="mb-2 h-4 w-3/4 animate-pulse rounded bg-gray-300" />
              <div className="h-4 w-1/2 animate-pulse rounded bg-gray-300" />
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>
    </div>
  );
}

