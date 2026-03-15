import { useEffect } from 'react';

import { ArtifactRenderer } from '@/components/ArtifactRenderer';
import { ChatStream } from '@/components/ChatStream';
import { InputBar } from '@/components/InputBar';
import { SessionSidebar } from '@/components/SessionSidebar';
import { Card } from '@/components/UI/Card';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUiStore } from '@/stores/uiStore';

export default function App() {
  const { messages } = useChat();
  const { sessions, activeSessionId, loadSessions } = useSession();
  const activePanel = useUiStore((state) => state.activePanel);
  const sidebarOpen = useUiStore((state) => state.sidebarOpen);
  const connectionStatus = useUiStore((state) => state.connectionStatus);
  useWebSocket();

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  const activeSession = sessions.find((session) => session.id === activeSessionId) ?? sessions[0];
  const flattenedArtifacts = messages.flatMap((message) => message.artifacts ?? []);
  const latestArtifact =
    flattenedArtifacts.length > 0 ? flattenedArtifacts[flattenedArtifacts.length - 1] : undefined;

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,107,53,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(24,78,67,0.16),_transparent_38%)]" />
      <div className="pointer-events-none fixed inset-0 bg-grid-fade bg-[size:28px_28px] opacity-40" />
      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 py-4 md:px-6 lg:px-8">
        <header className="mb-4 flex items-center justify-between rounded-[28px] border border-white/60 bg-sand/80 px-5 py-4 shadow-panel backdrop-blur">
          <div>
            <p className="font-display text-2xl tracking-tight">Vector Agents</p>
            <p className="text-sm text-ink/70">
              Research orchestration workspace for market and competitive intelligence
            </p>
          </div>
          <div className="rounded-full border border-ink/10 bg-white/70 px-4 py-2 text-xs uppercase tracking-[0.24em] text-ink/60">
            Milestone M1
          </div>
        </header>

        <main className="grid flex-1 gap-4 lg:grid-cols-[300px_minmax(0,1fr)_340px]">
          <aside className={sidebarOpen ? 'block' : 'hidden lg:block'}>
            <SessionSidebar />
          </aside>

          <section className="flex min-h-[70vh] flex-col gap-4">
            <Card className="flex-1 overflow-hidden">
              <div className="border-b border-ink/10 px-5 py-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Active session</p>
                  <div className="rounded-full border border-ink/10 bg-white/75 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-ink/55">
                    WS {connectionStatus}
                  </div>
                </div>
                <h1 className="mt-1 text-xl font-semibold">
                  {activeSession?.title ?? 'New intelligence workspace'}
                </h1>
                <p className="mt-2 text-sm text-ink/60">
                  {activeSession?.description ??
                    'Choose a session from the sidebar or create a new research thread.'}
                </p>
              </div>
              <ChatStream />
            </Card>
            <InputBar />
          </section>

          <aside className="space-y-4">
            <Card>
              <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Workbench</p>
              <h2 className="mt-2 font-display text-2xl leading-none">
                {activePanel === 'artifacts' ? 'Latest artifact' : 'System status'}
              </h2>
              <p className="mt-2 text-sm text-ink/70">
                Use this rail for artifact previews, agent state, and context controls as later
                milestones land.
              </p>
            </Card>

            <ArtifactRenderer artifact={latestArtifact} />
          </aside>
        </main>
      </div>
    </div>
  );
}
