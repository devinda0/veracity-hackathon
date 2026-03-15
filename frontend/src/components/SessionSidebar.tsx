import { Button } from '@/components/UI/Button';
import { Card } from '@/components/UI/Card';
import { useSession } from '@/hooks/useSession';
import { formatRelativeLabel } from '@/utils/format';
import { useUiStore } from '@/stores/uiStore';

export function SessionSidebar() {
  const {
    sessions,
    activeSessionId,
    createSession,
    deleteSession,
    error,
    loading,
    renameSession,
    selectSession,
  } = useSession();
  const toggleSidebar = useUiStore((state) => state.toggleSidebar);

  const handleCreateSession = () => {
    void createSession();
  };

  const handleSelectSession = (id: string) => {
    void selectSession(id);
  };

  const handleRenameSession = (id: string, title: string) => {
    const nextTitle = window.prompt('Rename session', title)?.trim();
    if (!nextTitle || nextTitle === title) {
      return;
    }

    void renameSession(id, nextTitle);
  };

  const handleDeleteSession = (id: string) => {
    const confirmed = window.confirm('Delete this session?');
    if (!confirmed) {
      return;
    }

    void deleteSession(id);
  };

  return (
    <Card className="h-full min-h-[70vh]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Sessions</p>
          <h2 className="mt-2 font-display text-3xl leading-none">Research threads</h2>
        </div>
        <button
          aria-label="Toggle sidebar"
          className="rounded-full border border-ink/10 px-3 py-2 text-xs uppercase tracking-[0.22em] text-ink/55 lg:hidden"
          onClick={toggleSidebar}
          type="button"
        >
          Close
        </button>
      </div>

      <p className="mt-3 text-sm text-ink/70">
        Session history is now backed by the API. Switch threads here to reload chat history and
        retarget the live WebSocket session.
      </p>

      {error ? (
        <div className="mt-4 rounded-[20px] border border-terracotta/20 bg-terracotta/10 px-4 py-3 text-sm text-terracotta">
          {error}
        </div>
      ) : null}

      <div className="mt-5 space-y-3">
        {sessions.length === 0 ? (
          <div className="rounded-[22px] border border-dashed border-ink/12 bg-white/45 px-4 py-5 text-sm text-ink/55">
            No sessions yet. Create a thread to start a research workspace.
          </div>
        ) : null}

        {sessions.map((session) => {
          const active = session.id === activeSessionId;

          return (
            <div
              className={`w-full rounded-[22px] border px-4 py-3 text-left transition ${
                active
                  ? 'border-spruce/20 bg-mist text-ink'
                  : 'border-ink/8 bg-white/60 text-ink/80 hover:border-ink/16 hover:bg-white'
              }`}
              key={session.id}
              onClick={() => handleSelectSession(session.id)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  handleSelectSession(session.id);
                }
              }}
              role="button"
              tabIndex={0}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <span className="block truncate font-medium">{session.title}</span>
                  <span className="mt-1 block text-[11px] uppercase tracking-[0.2em] text-ink/45">
                    {session.messageCount} message{session.messageCount === 1 ? '' : 's'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    aria-label={`Rename ${session.title}`}
                    className="rounded-full border border-ink/10 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-ink/45 hover:border-ink/20 hover:text-ink"
                    onClick={(event) => {
                      event.stopPropagation();
                      handleRenameSession(session.id, session.title);
                    }}
                    type="button"
                  >
                    Rename
                  </button>
                  <button
                    aria-label={`Delete ${session.title}`}
                    className="rounded-full border border-ink/10 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-ink/45 hover:border-terracotta/30 hover:text-terracotta"
                    onClick={(event) => {
                      event.stopPropagation();
                      handleDeleteSession(session.id);
                    }}
                    type="button"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <p className="mt-2 text-sm text-ink/60">
                {session.description ?? 'No description yet for this research thread.'}
              </p>
              <p className="mt-3 text-[11px] uppercase tracking-[0.2em] text-ink/40">
                Updated {formatRelativeLabel(session.updatedAt)}
              </p>
            </div>
          );
        })}
      </div>

      <div className="mt-5">
        <Button
          className="w-full"
          disabled={loading}
          onClick={handleCreateSession}
          variant="secondary"
        >
          {loading ? 'Working...' : 'New session'}
        </Button>
      </div>
    </Card>
  );
}
