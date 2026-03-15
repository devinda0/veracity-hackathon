import type { FormEvent } from 'react';

import { Button } from '@/components/UI/Button';
import { useChat } from '@/hooks/useChat';

export function InputBar() {
  const { draft, setDraft, submitDraft, isStreaming } = useChat();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void submitDraft();
  };

  return (
    <form className="panel-surface p-3" onSubmit={handleSubmit}>
      <div className="flex flex-col gap-3 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="mb-2 block text-xs uppercase tracking-[0.22em] text-ink/45">
            Research prompt
          </span>
          <textarea
            className="min-h-28 w-full resize-none rounded-[22px] border border-ink/10 bg-white/75 px-4 py-3 text-sm outline-none transition focus:border-spruce focus:ring-2 focus:ring-spruce/15"
            placeholder="Summarize market shifts in AI-native vector databases over the last 12 months."
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
        </label>

        <div className="flex items-center gap-3">
          <div className="hidden rounded-full border border-ink/10 bg-white/65 px-4 py-2 text-xs uppercase tracking-[0.24em] text-ink/50 lg:block">
            WebSocket-ready shell
          </div>
          <Button disabled={!draft.trim() || isStreaming} type="submit">
            {isStreaming ? 'Streaming...' : 'Send prompt'}
          </Button>
        </div>
      </div>
    </form>
  );
}
