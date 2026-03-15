interface WebSocketClient {
  close: () => void;
  onClose?: () => void;
  onOpen?: () => void;
}

export function createWebSocketClient(path: string): WebSocketClient {
  if (typeof window === 'undefined') {
    return {
      close: () => undefined,
    };
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${protocol}//${window.location.host}${path}`);

  const client: WebSocketClient = {
    close: () => socket.close(),
  };

  socket.addEventListener('open', () => client.onOpen?.());
  socket.addEventListener('close', () => client.onClose?.());

  return client;
}
