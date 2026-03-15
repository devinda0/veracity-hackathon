import { useEffect, useState } from 'react';

import { useChatStore, type AgentStatus } from '@/stores/chatStore';
import { Card } from '@/components/UI/Card';

function getStatusIcon(status: AgentStatus['status']): string {
  const icons: Record<AgentStatus['status'], string> = {
    pending: '⏳',
    running: '⚙️',
    completed: '✓',
    failed: '✗',
  };
  return icons[status];
}

function getStatusColor(status: AgentStatus['status']): string {
  const colors: Record<AgentStatus['status'], string> = {
    pending: 'text-gray-400',
    running: 'text-blue-600 animate-pulse',
    completed: 'text-green-600',
    failed: 'text-red-600',
  };
  return colors[status];
}

function extractDurationMs(agent: AgentStatus): number | null {
  const candidate = agent.result?.duration_ms;
  return typeof candidate === 'number' ? candidate : null;
}

export function AgentStatusPanel() {
  const { messages } = useChatStore();
  const [queryDurationSeconds, setQueryDurationSeconds] = useState(0);

  const lastMessage = messages[messages.length - 1];
  const agents = lastMessage?.agentTrace?.agents;
  const hasRunningAgents =
    agents?.some((agent) => agent.status === 'running' || agent.status === 'pending') ?? false;

  useEffect(() => {
    if (!lastMessage?.agentTrace) {
      setQueryDurationSeconds(0);
      return;
    }

    const traceDurationSeconds = Math.round((lastMessage.agentTrace.duration_ms ?? 0) / 1000);
    setQueryDurationSeconds(traceDurationSeconds);

    if (!hasRunningAgents) {
      return;
    }

    const startTime = Date.now() - (lastMessage.agentTrace.duration_ms ?? 0);
    const interval = window.setInterval(() => {
      setQueryDurationSeconds(Math.round((Date.now() - startTime) / 1000));
    }, 200);

    return () => window.clearInterval(interval);
  }, [lastMessage, hasRunningAgents]);

  return (
    <Card>
      <h3 className="text-lg font-bold text-ink">Agent Execution</h3>

      {(agents?.length ?? 0) > 0 ? (
        <>
          <div className="mt-4 space-y-3">
            {agents?.map((agent) => {
              const durationMs = extractDurationMs(agent);

              return (
                <div
                  key={agent.name}
                  className="flex items-center gap-3 rounded-lg border border-ink/8 bg-white/75 p-3"
                >
                  <span className={`text-2xl ${getStatusColor(agent.status)}`}>
                    {getStatusIcon(agent.status)}
                  </span>

                  <div className="min-w-0 flex-1">
                    <div className="font-medium capitalize text-ink">{agent.name.replace(/_/g, ' ')}</div>
                    <div className={`text-sm ${getStatusColor(agent.status)}`}>
                      {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                    </div>
                    {agent.status === 'failed' && agent.error && (
                      <div className="mt-1 text-xs text-red-600">{agent.error}</div>
                    )}
                  </div>

                  <div className="text-right text-xs text-ink/55">
                    <div className="uppercase tracking-wide">Duration</div>
                    <div className="font-semibold text-ink">
                      {durationMs !== null ? `${Math.round(durationMs / 1000)}s` : '—'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 border-t border-ink/8 pt-4 text-sm text-ink/60">
            Query duration: <span className="font-bold text-ink">{queryDurationSeconds}s</span>
          </div>
        </>
      ) : (
        <div className="py-8 text-center text-sm text-ink/45">No agents executed yet</div>
      )}
    </Card>
  );
}
