import { useEffect } from 'react';

import { AgentStatusPanel } from '@/components/AgentStatusPanel';
import { ArtifactRenderer } from '@/components/ArtifactRenderer';
import { BusinessContextPanel } from '@/components/BusinessContextPanel';
import { ChatStream } from '@/components/ChatStream';
import { InputBar } from '@/components/InputBar';
import { LoginPage } from '@/components/LoginPage';
import { SessionSidebar } from '@/components/SessionSidebar';
import { TraceViewer } from '@/components/TraceViewer';
import { Card } from '@/components/UI/Card';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAuthStore } from '@/stores/authStore';
import { useUiStore } from '@/stores/uiStore';

type ActivePanel = 'artifacts' | 'status' | 'context';

const PANEL_TABS: { id: ActivePanel; label: string; icon: string }[] = [
  { id: 'artifacts', label: 'Artifacts', icon: '◈' },
  { id: 'status', label: 'Agents', icon: '⚙' },
  { id: 'context', label: 'Context', icon: '📂' },
];

function MainApp() {
  const { messages } = useChat();
  const { sessions, activeSessionId, loadSessions } = useSession();
  const activePanel = useUiStore((state) => state.activePanel);
  const setActivePanel = useUiStore((state) => state.setActivePanel);
  const sidebarOpen = useUiStore((state) => state.sidebarOpen);
  const connectionStatus = useUiStore((state) => state.connectionStatus);
  const { logout, user } = useAuthStore();
  useWebSocket();

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  const activeSession = sessions.find((session) => session.id === activeSessionId) ?? sessions[0];
  const flattenedArtifacts = messages.flatMap((message) => message.artifacts ?? []);
  const latestArtifact =
    flattenedArtifacts.length > 0 ? flattenedArtifacts[flattenedArtifacts.length - 1] : undefined;

  // Grab trace from the last assistant message for TraceViewer
  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant');
  const latestTrace = lastAssistant?.agentTrace;

  const statusColor =
    connectionStatus === 'connected'
      ? 'text-spruce'
      : connectionStatus === 'connecting'
      ? 'text-accent'
      : 'text-ink/40';

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,107,53,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(24,78,67,0.16),_transparent_38%)]" />
      <div className="pointer-events-none fixed inset-0 bg-grid-fade bg-[size:28px_28px] opacity-40" />
      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 py-4 md:px-6 lg:px-8">
        <header className="mb-4 flex items-center justify-between rounded-[28px] border border-white/60 bg-sand/80 px-5 py-4 shadow-panel backdrop-blur">
          <div>
            <p className="font-display text-2xl tracking-tight">CoALA</p>
            <p className="text-sm text-ink/70">
              Research orchestration workspace for market and competitive intelligence
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div
              className={`rounded-full border border-ink/10 bg-white/70 px-4 py-2 text-xs uppercase tracking-[0.24em] ${statusColor}`}
            >
              WS {connectionStatus}
            </div>
            {user && (
              <div className="flex items-center gap-2 rounded-full border border-ink/10 bg-white/70 px-4 py-2">
                <span className="max-w-[140px] truncate text-xs text-ink/60">{user.email}</span>
                <button
                  onClick={logout}
                  className="text-xs font-semibold text-accent transition hover:underline"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </header>

        <main className="grid flex-1 gap-4 lg:grid-cols-[300px_minmax(0,1fr)_340px]">
          <aside className={sidebarOpen ? 'block' : 'hidden lg:block'}>
            <SessionSidebar />
          </aside>

          <section className="flex min-h-[70vh] flex-col gap-4">
            <Card className="flex-1 overflow-hidden">
              <div className="border-b border-ink/10 px-5 py-4">
                <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Active session</p>
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

          {/* Workbench rail */}
          <aside className="flex flex-col gap-4">
            {/* Panel tab switcher */}
            <div className="flex rounded-2xl border border-white/60 bg-sand/80 p-1 shadow-panel backdrop-blur">
              {PANEL_TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActivePanel(tab.id)}
                  className={`flex flex-1 items-center justify-center gap-1.5 rounded-xl px-3 py-2 text-xs font-semibold transition ${
                    activePanel === tab.id
                      ? 'bg-ink text-canvas shadow-sm'
                      : 'text-ink/55 hover:text-ink'
                  }`}
                >
                  <span aria-hidden>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Panel body */}
            <div className="flex flex-col gap-4">
              {activePanel === 'artifacts' && (
                <>
                  <Card>
                    <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Workbench</p>
                    <h2 className="mt-2 font-display text-2xl leading-none">Latest artifact</h2>
                    <p className="mt-2 text-sm text-ink/70">
                      Visual outputs from agent runs appear here.
                    </p>
                  </Card>
                  <ArtifactRenderer artifact={latestArtifact} />
                  {latestTrace && (
                    <Card>
                      <TraceViewer trace={latestTrace} />
                    </Card>
                  )}
                </>
              )}

              {activePanel === 'status' && (
                <Card>
                  <p className="mb-4 text-xs uppercase tracking-[0.22em] text-ink/45">
                    Agent execution
                  </p>
                  <AgentStatusPanel />
                </Card>
              )}

              {activePanel === 'context' && (
                <Card>
                  <p className="mb-4 text-xs uppercase tracking-[0.22em] text-ink/45">
                    Business context
                  </p>
                  <BusinessContextPanel />
                </Card>
              )}
            </div>
          </aside>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const { hydrate, token } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  if (!token) {
    return <LoginPage />;
  }

  return <MainApp />;
}
