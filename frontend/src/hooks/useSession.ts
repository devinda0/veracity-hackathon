import { useSessionStore } from '@/stores/sessionStore';

export function useSession() {
  const error = useSessionStore((state) => state.error);
  const sessions = useSessionStore((state) => state.sessions);
  const activeSessionId = useSessionStore((state) => state.activeSessionId);
  const loading = useSessionStore((state) => state.loading);
  const selectSession = useSessionStore((state) => state.selectSession);
  const createSession = useSessionStore((state) => state.createSession);
  const deleteSession = useSessionStore((state) => state.deleteSession);
  const loadSessions = useSessionStore((state) => state.loadSessions);
  const renameSession = useSessionStore((state) => state.renameSession);

  return {
    activeSessionId,
    createSession,
    deleteSession,
    error,
    loadSessions,
    loading,
    renameSession,
    selectSession,
    sessions,
  };
}
