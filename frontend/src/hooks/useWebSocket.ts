import { useEffect, useRef, useCallback } from 'react'
import type { Artifact, AgentTrace } from '../stores/chatStore'
import { useChatStore } from '../stores/chatStore'
import { useUiStore } from '../stores/uiStore'
import { v4 as uuidv4 } from 'uuid'

interface WSMessage {
  type: 'status' | 'artifact' | 'thinking' | 'final' | 'error'
  session_id: string
  content: string
  agent?: string
  metadata?: Record<string, unknown>
  timestamp: string
}

const RECONNECT_DELAY_MS = 3000
const MAX_RECONNECT_ATTEMPTS = 5

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const messageQueueRef = useRef<string[]>([])
  const connectionStateRef = useRef<'connecting' | 'connected' | 'disconnected'>('disconnected')

  const { sessionId, addMessage, addArtifact, setLoading, setError } = useChatStore()
  const { setConnectionStatus } = useUiStore()

  const connect = useCallback(() => {
    if (!sessionId) return

    connectionStateRef.current = 'connecting'
    setConnectionStatus('connecting')

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws/chat/${sessionId}`

    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      console.log('[WebSocket] Connected')
      connectionStateRef.current = 'connected'
      setConnectionStatus('connected')
      reconnectAttemptsRef.current = 0

      // Flush message queue
      while (messageQueueRef.current.length > 0) {
        const msg = messageQueueRef.current.shift()
        if (msg) wsRef.current?.send(msg)
      }
    }

    wsRef.current.onmessage = (event) => {
      try {
        const wsMsg: WSMessage = JSON.parse(event.data)
        const messageId = uuidv4()

        switch (wsMsg.type) {
          case 'status':
            // Agent status update
            console.log(`[Agent ${wsMsg.agent}] ${wsMsg.content}`)
            break

          case 'thinking':
            // Agent reasoning
            addMessage({
              id: messageId,
              role: 'assistant',
              content: wsMsg.content,
              timestamp: new Date(wsMsg.timestamp),
            })
            break

          case 'artifact': {
            // Add artifact to last message
            const artifact: Artifact = {
              id: uuidv4(),
              type: wsMsg.content,
              title: wsMsg.metadata?.title as string,
              data: wsMsg.metadata?.data as Record<string, unknown>,
            }
            const lastMsg = useChatStore.getState().messages[useChatStore.getState().messages.length - 1]
            if (lastMsg) {
              addArtifact(lastMsg.id, artifact)
            }
            break
          }

          case 'final': {
            // Final response
            addMessage({
              id: messageId,
              role: 'assistant',
              content: wsMsg.content,
              timestamp: new Date(wsMsg.timestamp),
              agentTrace: wsMsg.metadata?.trace as AgentTrace,
              tokensUsed: wsMsg.metadata?.tokens_used as number,
              cost: wsMsg.metadata?.cost as number,
            })
            setLoading(false)
            break
          }

          case 'error':
            setError(wsMsg.content)
            setLoading(false)
            break
        }
      } catch (e) {
        console.error('[WebSocket] Parse error:', e)
      }
    }

    wsRef.current.onerror = (event) => {
      console.error('[WebSocket] Error:', event)
      setError('WebSocket error occurred')
    }

    wsRef.current.onclose = () => {
      console.log('[WebSocket] Disconnected')
      connectionStateRef.current = 'disconnected'
      setConnectionStatus('disconnected')
      setLoading(false)

      // Auto-reconnect
      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttemptsRef.current++
        setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }
  }, [sessionId, addMessage, addArtifact, setLoading, setError, setConnectionStatus])

  const send = useCallback((message: string) => {
    if (connectionStateRef.current === 'connected' && wsRef.current) {
      wsRef.current.send(JSON.stringify({ content: message }))
    } else {
      messageQueueRef.current.push(JSON.stringify({ content: message }))
      if (connectionStateRef.current === 'disconnected') {
        connect()
      }
    }
  }, [connect])

  useEffect(() => {
    if (sessionId) {
      connect()
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [sessionId, connect])

  return {
    send,
    isConnected: connectionStateRef.current === 'connected',
    status: connectionStateRef.current,
  }
}

