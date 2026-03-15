import type { Message } from '@/stores/chatStore';

import { ArtifactRenderer } from '@/components/ArtifactRenderer';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <article className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-[28px] px-5 py-4 ${
          isUser
            ? 'bg-spruce text-white shadow-lg'
            : 'border border-ink/8 bg-white/75 text-ink shadow-sm'
        }`}
      >
        <div className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.22em] opacity-65">
          <span>{message.role}</span>
          <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
        <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>

        {message.artifacts?.length ? (
          <div className="mt-4 space-y-3">
            {message.artifacts.map((artifact) => (
              <ArtifactRenderer key={artifact.id} artifact={artifact} />
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}

