import { useEffect, useRef, useState } from 'react';

import { useChatStore } from '@/stores/chatStore';

const STATUS_STYLES: Record<string, { dot: string; label: string; ring: string }> = {
  pending: { dot: 'bg-ink/20', label: 'text-ink/40', ring: '' },
  running: { dot: 'bg-accent animate-pulse', label: 'text-accent', ring: 'ring-2 ring-accent/30' },
  completed: { dot: 'bg-spruce', label: 'text-spruce', ring: '' },
  failed: { dot: 'bg-red-500', label: 'text-red-600', ring: '' },
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Queued',
  running: 'Running…',
  completed: 'Done',
  failed: 'Failed',
};

function formatAgentName(name: string) {
  return name
    .replace(/_agent$/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function AgentStatusPanel() {
  const liveAgentStatuses = useChatStore((state) => state.liveAgentStatuses);
  const messages = useChatStore((state) => state.messages);
  const loading = useChatStore((state) => state.loading);

  const [elapsedSec, setElapsedSec] = useState(0);
  const startRef = useRef<number | null>(null);

  // Start/stop the query timer
  useEffect(() => {
    if (loading) {
      startRef.current = Date.now();
      setElapsedSec(0);
      const id = window.setInterval(() => {
        setElapsedSec(Math.round((Date.now() - (startRef.current ?? Date.now())) / 1000));
      }, 500);
      return () => window.clearInterval(id);
    }
  }, [loading]);

  // Use agentTrace from last assistant message when not loading
  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant');
  const traceAgents = lastAssistant?.agentTrace?.agents ?? [];
  const traceDurationMs = lastAssistant?.agentTrace?.duration_ms;

  const agents = loading ? liveAgentStatuses : traceAgents;
  const hasData = agents.length > 0;

  return (
    <div className="flex flex-col gap-4">
      {/* Header stats */}
      {hasData && (
        <div className="flex items-center justify-between rounded-2xl border border-ink/10 bg-sand px-4 py-3 text-sm">
          <span className="text-ink/60">
            {loading ? 'Query running' : 'Last query'}
          </span>
          <span className="font-semibold text-ink">
            {loading
              ? `${elapsedSec}s`
              : traceDurationMs != null
              ? `${(traceDurationMs / 1000).toFixed(1)}s`
              : '—'}
          </span>
        </div>
      )}

      {/* Agent list */}
      {hasData ? (
        <div className="flex flex-col gap-2">
          {agents.map((agent) => {
            const s = STATUS_STYLES[agent.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={agent.name}
                className={`flex items-center gap-3 rounded-2xl border border-ink/10 bg-white/60 px-4 py-3 transition ${s.ring}`}
              >
                <span className={`h-2.5 w-2.5 flex-shrink-0 rounded-full ${s.dot}`} />

                <div className="flex flex-1 flex-col min-w-0">
                  <span className="truncate text-sm font-medium text-ink">
                    {formatAgentName(agent.name)}
                  </span>
                  {agent.status === 'failed' && agent.error && (
                    <span className="truncate text-xs text-red-500">{agent.error}</span>
                  )}
                </div>

                <div className="flex flex-col items-end gap-0.5 flex-shrink-0">
                  <span className={`text-xs font-semibold uppercase tracking-wide ${s.label}`}>
                    {STATUS_LABELS[agent.status] ?? agent.status}
                  </span>
                  {agent.duration_ms != null && agent.status === 'completed' && (
                    <span className="text-[11px] text-ink/40">{agent.duration_ms}ms</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-ink/10 bg-sand/50 py-12 text-center">
          <span className="text-2xl">🤖</span>
          <p className="text-sm text-ink/50">No agents have run yet.</p>
          <p className="text-xs text-ink/35">Ask a question to see execution status here.</p>
        </div>
      )}
    </div>
  );
}
