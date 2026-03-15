import { useEffect, useState } from 'react';

import { createWebSocketClient } from '@/utils/websocket';

export function useWebSocket(path = '/ws') {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const client = createWebSocketClient(path);

    client.onOpen = () => setConnected(true);
    client.onClose = () => setConnected(false);

    return () => {
      client.close();
    };
  }, [path]);

  return { connected };
}

