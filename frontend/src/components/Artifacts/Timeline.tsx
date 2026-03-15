import { useState } from 'react';

import type { Artifact } from '@/stores/chatStore';
import { Card } from '@/components/UI/Card';

interface TimelineEvent {
  date: string;
  event: string;
  confidence: number;
  details?: string;
}

interface TimelineData {
  events?: TimelineEvent[];
}

interface TimelineProps {
  artifact: Artifact;
}

function confidenceTone(conf: number) {
  if (conf >= 80)
    return {
      dot: 'bg-emerald-500',
      badge: 'bg-emerald-100 text-emerald-700',
    };
  if (conf >= 60)
    return {
      dot: 'bg-amber-400',
      badge: 'bg-amber-100 text-amber-700',
    };
  return {
    dot: 'bg-rose-500',
    badge: 'bg-rose-100 text-rose-700',
  };
}

export function Timeline({ artifact }: TimelineProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const data = (artifact.data ?? {}) as TimelineData;
  const events: TimelineEvent[] = data.events ?? [];

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>

      {events.length > 0 ? (
        <div className="relative mt-6 pl-6">
          {/* Vertical rule */}
          <div className="absolute bottom-0 left-[11px] top-0 w-0.5 bg-ink/10" />

          <div className="space-y-6">
            {events.map((ev, idx) => {
              const tone = confidenceTone(ev.confidence);
              const isActive = activeIndex === idx;

              return (
                <div
                  key={idx}
                  className="relative cursor-pointer"
                  onMouseEnter={() => setActiveIndex(idx)}
                  onMouseLeave={() => setActiveIndex(null)}
                >
                  {/* Dot */}
                  <div
                    className={`absolute -left-6 top-1.5 h-3.5 w-3.5 rounded-full border-2 border-white shadow ${tone.dot}`}
                  />

                  {/* Card body */}
                  <div className="rounded-lg border border-ink/8 bg-white/75 p-4 transition hover:border-ink/20 hover:shadow-sm">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-medium text-ink">{ev.event}</p>
                      <span
                        className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${tone.badge}`}
                      >
                        {ev.confidence}%
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-ink/50">{ev.date}</p>

                    {isActive && (
                      <p className="mt-2 border-t border-ink/8 pt-2 text-sm text-ink/70">
                        {ev.details ?? `Confidence level: ${ev.confidence}%`}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <p className="mt-6 py-8 text-center text-sm text-ink/50">No timeline events available</p>
      )}
    </Card>
  );
}
