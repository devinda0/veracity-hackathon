import { useState } from 'react';

import { formatDistanceToNow } from 'date-fns';

import type { Message } from '@/types';
import { ArtifactRenderer } from '@/components/ArtifactRenderer';

interface AgentTraceStatus {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

interface MessageMeta extends Message {
  agent?: string;
  citations?: string[];
  cost?: number;
  tokensUsed?: number;
  agentTrace?: {
    agents: AgentTraceStatus[];
  };
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [expandTrace, setExpandTrace] = useState(false);
  const typedMessage = message as MessageMeta;
  const isUser = typedMessage.role === 'user';
  const assistantLabel = typedMessage.agent ?? 'assistant';

  return (
    <div className={`flex gap-3 md:gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm md:h-9 md:w-9 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gradient-to-r from-purple-400 to-pink-500 text-white'
        }`}
      >
        {isUser ? '👤' : '🤖'}
      </div>

      <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block w-full max-w-full rounded-lg p-4 text-left sm:max-w-2xl ${
            isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'
          }`}
        >
          <div className="text-sm leading-6">{typedMessage.content}</div>

          {typedMessage.artifacts && typedMessage.artifacts.length > 0 && (
            <div className="mt-4 space-y-3">
              {typedMessage.artifacts.map((artifact) => (
                <ArtifactRenderer key={artifact.id} artifact={artifact} />
              ))}
            </div>
          )}

          {typedMessage.citations && typedMessage.citations.length > 0 && (
            <div className="pt-3 mt-3 text-xs border-t border-gray-300/60">
              <p className="mb-1 font-medium text-gray-600">Citations</p>
              <ul className="space-y-1 text-gray-500">
                {typedMessage.citations.map((citation) => (
                  <li key={citation}>• {citation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : ''}`}>
          {!isUser && `${assistantLabel} • `}
          {formatDistanceToNow(new Date(typedMessage.timestamp), { addSuffix: true })}
          {typedMessage.tokensUsed ? ` • ${typedMessage.tokensUsed} tokens` : ''}
          {typedMessage.cost ? ` • $${typedMessage.cost.toFixed(3)}` : ''}
        </div>

        {typedMessage.agentTrace && (
          <div className="mt-3">
            <button
              onClick={() => setExpandTrace((prev) => !prev)}
              className="text-xs text-blue-600 hover:text-blue-800"
              type="button"
            >
              {expandTrace ? '▼' : '▶'} Agent trace ({typedMessage.agentTrace.agents.length} agents)
            </button>

            {expandTrace && (
              <div className="p-2 mt-2 text-xs border border-gray-200 rounded bg-gray-50">
                {typedMessage.agentTrace.agents.map((agent) => (
                  <div key={agent.name} className="flex items-center gap-2 mb-1">
                    <span
                      className={`h-2 w-2 rounded-full ${
                        agent.status === 'completed'
                          ? 'bg-green-500'
                          : agent.status === 'failed'
                            ? 'bg-red-500'
                            : 'bg-yellow-500'
                      }`}
                    />
                    <span>
                      {agent.name}: {agent.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

