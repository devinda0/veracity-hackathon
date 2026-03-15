import { useState } from 'react';

import { Card } from '@/components/UI/Card';

interface TimelineEvent {
  date: string;
  event: string;
  confidence: number;
  details?: string;
}

interface TimelineProps {
  data: unknown;
  title: string;
}

function confidenceTone(confidence: number) {
  if (confidence >= 80) {
    return {
      dot: 'bg-emerald-500',
      badge: 'bg-emerald-100 text-emerald-700',
      label: 'high',
    };
  }

  if (confidence >= 60) {
    return {
      dot: 'bg-amber-500',
      badge: 'bg-amber-100 text-amber-700',
      label: 'medium',
    };
  }

  return {
    dot: 'bg-rose-500',
    badge: 'bg-rose-100 text-rose-700',
    label: 'low',
  };
}

export function Timeline({ data, title }: TimelineProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const events = ((data as { events?: TimelineEvent[] })?.events ?? []) as TimelineEvent[];

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Timeline</p>
      <h3 className="mt-2 text-lg font-semibold">{title}</h3>

      {events.length > 0 ? (
        <div className="relative mt-5">
          <div className="absolute bottom-0 left-5 top-0 w-[2px] bg-ink/10" />

          <div className="space-y-5 pl-12">
            {events.map((timelineEvent, index) => {
              const tone = confidenceTone(timelineEvent.confidence);

              return (
                <div
                  className="relative"
                  key={`${timelineEvent.date}-${timelineEvent.event}-${index}`}
                  onMouseEnter={() => setActiveIndex(index)}
                  onMouseLeave={() => setActiveIndex((prev) => (prev === index ? null : prev))}
                >
                  <div className={`absolute -left-9 top-1 h-4 w-4 rounded-full border-2 border-white ${tone.dot}`} />

                  <div className="rounded-[16px] border border-ink/8 bg-white/75 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm font-semibold text-ink">{timelineEvent.event}</p>
                      <span className={`rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${tone.badge}`}>
                        {tone.label}
                      </span>
                    </div>
                    <p className="mt-1 text-xs uppercase tracking-[0.14em] text-ink/55">{timelineEvent.date}</p>
                    <p className="mt-2 text-xs text-ink/60">Confidence: {timelineEvent.confidence}%</p>

                    {activeIndex === index ? (
                      <div className="mt-2 rounded-[12px] border border-ink/8 bg-mist px-3 py-2 text-xs text-ink/70">
                        {timelineEvent.details ?? `Event confidence score is ${timelineEvent.confidence}%.`}
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="mt-4 rounded-[16px] border border-ink/8 bg-white/75 py-10 text-center text-sm text-ink/55">
          No timeline events
        </div>
      )}
    </Card>
  );
}
