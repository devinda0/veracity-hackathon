import { Button } from '@/components/UI/Button';
import { Card } from '@/components/UI/Card';
import { useSession } from '@/hooks/useSession';
import { useUiStore } from '@/stores/uiStore';

export function SessionSidebar() {
  const { sessions, activeSessionId, createSession, selectSession } = useSession();
  const toggleSidebar = useUiStore((state) => state.toggleSidebar);

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
        Placeholder session management built on Zustand. CRUD flows will attach to backend APIs in
        issue #12.
      </p>

      <div className="mt-5 space-y-3">
        {sessions.map((session) => {
          const active = session.id === activeSessionId;

          return (
            <button
              className={`w-full rounded-[22px] border px-4 py-3 text-left transition ${
                active
                  ? 'border-spruce/20 bg-mist text-ink'
                  : 'border-ink/8 bg-white/60 text-ink/80 hover:border-ink/16 hover:bg-white'
              }`}
              key={session.id}
              onClick={() => selectSession(session.id)}
              type="button"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-medium">{session.title}</span>
                <span className="text-[11px] uppercase tracking-[0.2em] text-ink/45">
                  {session.status}
                </span>
              </div>
              <p className="mt-2 text-sm text-ink/60">{session.summary}</p>
            </button>
          );
        })}
      </div>

      <div className="mt-5">
        <Button className="w-full" onClick={createSession} variant="secondary">
          New session
        </Button>
      </div>
    </Card>
  );
}

