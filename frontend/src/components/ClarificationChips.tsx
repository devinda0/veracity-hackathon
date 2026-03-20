import { useChatStore, type ClarificationOption } from '@/stores/chatStore';
import { useWebSocket } from '@/hooks/useWebSocket';

interface ClarificationChipsProps {
  options: ClarificationOption[];
}

export function ClarificationChips({ options }: ClarificationChipsProps) {
  const addMessage = useChatStore((state) => state.addMessage);
  const clearLiveAgentStatuses = useChatStore((state) => state.clearLiveAgentStatuses);
  const setClarificationOptions = useChatStore((state) => state.setClarificationOptions);
  const setLoading = useChatStore((state) => state.setLoading);
  const { send } = useWebSocket();

  function handleSelect(option: ClarificationOption) {
    const ts = new Date();
    addMessage({
      id: `user-clarify-${option.id}`,
      role: 'user',
      content: option.query,
      timestamp: ts,
    });
    clearLiveAgentStatuses();
    setClarificationOptions(null);
    setLoading(true);
    send(option.query);
  }

  function handleDismiss() {
    setClarificationOptions(null);
  }

  return (
    <div className="rounded-2xl border border-accent/30 bg-accent/5 p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-widest text-accent/80">
          Did you mean?
        </p>
        <button
          onClick={handleDismiss}
          aria-label="Dismiss clarification options"
          className="rounded-full p-1 text-ink/40 transition hover:bg-ink/10 hover:text-ink"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
            <path d="M11 3L3 11M3 3l8 8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" fill="none" />
          </svg>
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option.id}
            onClick={() => handleSelect(option)}
            className="rounded-full border border-accent/40 bg-white/80 px-4 py-1.5 text-sm font-medium text-accent shadow-sm transition hover:border-accent hover:bg-accent hover:text-white focus:outline-none focus:ring-2 focus:ring-accent/50"
          >
            {option.text}
          </button>
        ))}
      </div>
    </div>
  );
}
