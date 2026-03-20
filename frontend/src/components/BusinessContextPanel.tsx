import { useEffect, useState } from 'react';

import { useChatStore } from '@/stores/chatStore';

interface ContextItem {
  context_id: string;
  type: 'document' | 'url' | 'text';
  source: string;
  chunk_count: number;
  created_at: string;
}

const TYPE_ICONS: Record<string, string> = {
  document: '📄',
  url: '🔗',
  text: '📝',
};

const TYPE_LABELS: Record<string, string> = {
  document: 'Document',
  url: 'URL',
  text: 'Text',
};

export function BusinessContextPanel() {
  const sessionId = useChatStore((state) => state.sessionId);
  const [contexts, setContexts] = useState<ContextItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      void fetchContexts();
    } else {
      setContexts([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function fetchContexts() {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v1/sessions/${sessionId}/context`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as { contexts: ContextItem[] };
      setContexts(data.contexts ?? []);
    } catch {
      setError('Could not load context. The backend may not be running yet.');
    } finally {
      setLoading(false);
    }
  }

  async function deleteContext(contextId: string) {
    if (!sessionId) return;
    setRemovingId(contextId);
    try {
      const token = localStorage.getItem('token');
      await fetch(`/api/v1/sessions/${sessionId}/context/${contextId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setContexts((prev) => prev.filter((c) => c.context_id !== contextId));
    } catch {
      // Silently fail on delete — item will re-appear on next refresh
    } finally {
      setRemovingId(null);
    }
  }

  const totalChunks = contexts.reduce((sum, c) => sum + c.chunk_count, 0);

  return (
    <div className="flex flex-col gap-4">
      {/* Summary bar */}
      {contexts.length > 0 && (
        <div className="flex items-center justify-between rounded-2xl border border-ink/10 bg-sand px-4 py-3 text-sm">
          <span className="text-ink/60">
            {contexts.length} source{contexts.length !== 1 ? 's' : ''}
          </span>
          <span className="font-semibold text-ink">{totalChunks} chunks indexed</span>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex flex-col gap-2">
          {[1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-2xl bg-ink/10" />
          ))}
        </div>
      ) : error ? (
        <div className="rounded-2xl border border-ink/10 bg-sand/50 px-4 py-6 text-center text-sm text-ink/50">
          {error}
        </div>
      ) : contexts.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-ink/10 bg-sand/50 py-12 text-center">
          <span className="text-2xl">📂</span>
          <p className="text-sm text-ink/50">No business context yet.</p>
          <p className="text-xs text-ink/35">Upload documents, paste URLs, or add text via the input bar.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {contexts.map((ctx) => (
            <div
              key={ctx.context_id}
              className="flex items-center gap-3 rounded-2xl border border-ink/10 bg-white/60 px-4 py-3"
            >
              <span className="flex-shrink-0 text-xl" aria-hidden>
                {TYPE_ICONS[ctx.type] ?? '📌'}
              </span>

              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-ink" title={ctx.source}>
                  {ctx.source}
                </p>
                <p className="text-xs text-ink/45">
                  {TYPE_LABELS[ctx.type] ?? ctx.type} · {ctx.chunk_count} chunks ·{' '}
                  {new Date(ctx.created_at).toLocaleDateString()}
                </p>
              </div>

              <button
                onClick={() => void deleteContext(ctx.context_id)}
                disabled={removingId === ctx.context_id}
                aria-label={`Remove ${ctx.source}`}
                className="flex-shrink-0 rounded-full px-3 py-1 text-xs font-medium text-red-500 transition hover:bg-red-50 hover:text-red-700 disabled:opacity-40"
              >
                {removingId === ctx.context_id ? '…' : 'Remove'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Refresh */}
      {!loading && (
        <button
          onClick={() => void fetchContexts()}
          className="rounded-full border border-ink/15 bg-white/60 px-4 py-2 text-xs font-medium text-ink/60 transition hover:bg-mist hover:text-ink"
        >
          Refresh
        </button>
      )}
    </div>
  );
}
