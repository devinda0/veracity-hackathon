import { useSessionStore } from '@/stores/sessionStore';

export function useSession() {
  const sessions = useSessionStore((state) => state.sessions);
  const activeSessionId = useSessionStore((state) => state.activeSessionId);
  const selectSession = useSessionStore((state) => state.selectSession);
  const createSession = useSessionStore((state) => state.createSession);
  const ensureSeedData = useSessionStore((state) => state.ensureSeedData);

  return {
    activeSessionId,
    createSession,
    ensureSeedData,
    selectSession,
    sessions,
  };
}

