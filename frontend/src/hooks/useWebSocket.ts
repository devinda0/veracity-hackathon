import { useCallback, useEffect, useRef, useState } from 'react';

import type { AgentTrace, Artifact } from '@/stores/chatStore';
import { useChatStore } from '@/stores/chatStore';
import { useUiStore } from '@/stores/uiStore';

interface WSMessage {
  type: 'status' | 'artifact' | 'thinking' | 'final' | 'error';
  session_id: string;
  content: string;
  agent?: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

const RECONNECT_DELAY_MS = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

  const sessionId = useChatStore((state) => state.sessionId);
  const addMessage = useChatStore((state) => state.addMessage);
  const addArtifact = useChatStore((state) => state.addArtifact);
  const setLoading = useChatStore((state) => state.setLoading);
  const setError = useChatStore((state) => state.setError);
  const setConnectionStatus = useUiStore((state) => state.setConnectionStatus);

  const connect = useCallback(() => {
    if (!sessionId || typeof window === 'undefined') {
      return;
    }

    setStatus('connecting');
    setConnectionStatus('connecting');

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/chat?session_id=${encodeURIComponent(sessionId)}`;

    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setStatus('connected');
      setConnectionStatus('connected');
      reconnectAttemptsRef.current = 0;
    };

    wsRef.current.onmessage = (event) => {
      try {
        const wsMsg: WSMessage = JSON.parse(event.data);
        const messageId = crypto.randomUUID();

        switch (wsMsg.type) {
          case 'status':
            break;

          case 'thinking':
            addMessage({
              id: messageId,
              role: 'assistant',
              content: wsMsg.content,
              timestamp: new Date(wsMsg.timestamp),
            });
            break;

          case 'artifact': {
            const artifact: Artifact = {
              id: crypto.randomUUID(),
              type: wsMsg.content,
              title: wsMsg.metadata?.title as string,
              data: wsMsg.metadata?.data as Record<string, unknown>,
            };
            const lastMsg =
              useChatStore.getState().messages[useChatStore.getState().messages.length - 1];
            if (lastMsg) {
              addArtifact(lastMsg.id, artifact);
            }
            break;
          }

          case 'final': {
            addMessage({
              id: messageId,
              role: 'assistant',
              content: wsMsg.content,
              timestamp: new Date(wsMsg.timestamp),
              agentTrace: wsMsg.metadata?.trace as AgentTrace,
              tokensUsed: wsMsg.metadata?.tokens_used as number,
              cost: wsMsg.metadata?.cost as number,
            });
            setLoading(false);
            break;
          }

          case 'error':
            setError(wsMsg.content);
            setLoading(false);
            break;
        }
      } catch {
        setError('Failed to parse WebSocket message');
      }
    };

    wsRef.current.onerror = () => {
      setError('WebSocket error occurred');
    };

    wsRef.current.onclose = () => {
      setStatus('disconnected');
      setConnectionStatus('disconnected');
      setLoading(false);

      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttemptsRef.current += 1;
        window.setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };
  }, [sessionId, addMessage, addArtifact, setLoading, setError, setConnectionStatus]);

  const send = useCallback(
    (message: string) => {
      if (!sessionId) {
        return;
      }

      if (status === 'connected' && wsRef.current) {
        wsRef.current.send(
          JSON.stringify({
            type: 'status',
            session_id: sessionId,
            content: message,
            agent: 'client',
            timestamp: new Date().toISOString(),
          }),
        );
      }
    },
    [sessionId, status],
  );

  useEffect(() => {
    if (!sessionId) {
      wsRef.current?.close();
      setStatus('disconnected');
      setConnectionStatus('disconnected');
      return;
    }

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, [sessionId, connect, setConnectionStatus]);

  return {
    send,
    isConnected: status === 'connected',
    status,
  };
}
