import { useState } from 'react';

import type { AgentTrace } from '@/stores/chatStore';

interface TraceNode {
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration_ms: number;
  tokens: number;
  cost: number;
  error?: string;
  children?: TraceNode[];
  tools_called?: Array<{ name: string; duration_ms: number }>;
}

interface TraceViewerProps {
  trace: AgentTrace;
}

const STATUS_BADGE: Record<string, string> = {
  completed: 'bg-spruce/10 text-spruce',
  failed: 'bg-red-50 text-red-600',
  running: 'bg-accent/10 text-accent',
  pending: 'bg-ink/10 text-ink/50',
};

function AgentNode({ node, depth = 0 }: { node: TraceNode; depth?: number }) {
  const [expanded, setExpanded] = useState(depth === 0);
  const hasChildren = (node.children?.length ?? 0) > 0 || (node.tools_called?.length ?? 0) > 0;

  return (
    <div className={depth > 0 ? 'ml-4 border-l border-ink/10 pl-3' : ''}>
      <div
        className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 transition hover:bg-ink/5"
        onClick={() => hasChildren && setExpanded((e) => !e)}
        role={hasChildren ? 'button' : undefined}
        tabIndex={hasChildren ? 0 : undefined}
        onKeyDown={(e) => e.key === 'Enter' && hasChildren && setExpanded((ex) => !ex)}
      >
        {hasChildren ? (
          <span className="w-4 flex-shrink-0 text-center text-xs text-ink/40">
            {expanded ? '▾' : '▸'}
          </span>
        ) : (
          <span className="w-4 flex-shrink-0" />
        )}

        <code className="flex-shrink-0 rounded bg-ink/8 px-1.5 py-0.5 text-xs font-mono text-ink/80">
          {node.agent}
        </code>

        <span
          className={`flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${
            STATUS_BADGE[node.status] ?? STATUS_BADGE.pending
          }`}
        >
          {node.status}
        </span>

        <span className="ml-auto flex-shrink-0 text-xs text-ink/40">{node.duration_ms}ms</span>

        {node.tokens > 0 && (
          <span className="flex-shrink-0 text-xs text-ink/40">{node.tokens} tok</span>
        )}

        {node.cost > 0 && (
          <span className="flex-shrink-0 text-xs text-ink/40">${node.cost.toFixed(4)}</span>
        )}
      </div>

      {expanded && (
        <div className="mt-1">
          {node.error && (
            <div className="mx-3 mb-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 font-mono text-xs text-red-700">
              {node.error}
            </div>
          )}

          {(node.tools_called?.length ?? 0) > 0 && (
            <div className="mx-3 mb-2 rounded-xl border border-ink/10 bg-sand/60 px-3 py-2">
              <p className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-ink/40">
                Tools called
              </p>
              <div className="flex flex-col gap-1">
                {node.tools_called!.map((tool, i) => (
                  <div key={i} className="flex items-center justify-between text-xs text-ink/70">
                    <code className="font-mono">{tool.name}</code>
                    <span className="text-ink/40">{tool.duration_ms}ms</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {node.children?.map((child, i) => (
            <AgentNode key={i} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function agentStatusToTraceNode(
  agent: AgentTrace['agents'][number],
  totalCost?: number,
): TraceNode {
  const agentCount = 1;
  return {
    agent: agent.name,
    status: agent.status,
    duration_ms: agent.duration_ms ?? 0,
    tokens: 0,
    cost: totalCost ? totalCost / agentCount : 0,
    error: agent.error,
  };
}

export function TraceViewer({ trace }: TraceViewerProps) {
  const nodes: TraceNode[] = trace.agents.map((a) => agentStatusToTraceNode(a));

  if (nodes.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-widest text-ink/40">Execution trace</p>
        <span className="text-xs text-ink/40">
          {(trace.duration_ms / 1000).toFixed(2)}s total
        </span>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-ink/10 bg-sand/50 p-3 font-mono text-sm">
        {nodes.map((node, i) => (
          <AgentNode key={i} node={node} />
        ))}
      </div>
    </div>
  );
}
