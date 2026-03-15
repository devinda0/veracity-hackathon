import { MessageBubble } from '@/components/MessageBubble';
import { useChat } from '@/hooks/useChat';

export function ChatStream() {
  const { messages, loading } = useChat();

  if (messages.length === 0) {
    return (
      <div className="flex h-full min-h-[480px] items-center justify-center p-8">
        <div className="max-w-md text-center">
          <p className="text-xs uppercase tracking-[0.24em] text-ink/45">Empty state</p>
          <h2 className="mt-3 font-display text-4xl leading-none">Ask for a market brief</h2>
          <p className="mt-4 text-sm text-ink/70">
            The app shell is ready. Once API routes and streaming land, this column will render live
            assistant responses, artifact references, and trace details.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-[480px] flex-col gap-4 overflow-y-auto px-5 py-5">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {loading ? (
        <div className="w-fit rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-sm text-accent">
          Agents are streaming updates...
        </div>
      ) : null}
    </div>
  );
}

