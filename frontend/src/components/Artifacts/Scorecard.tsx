import type { Artifact } from '@/stores/chatStore';

import { Card } from '@/components/UI/Card';

interface ScorecardRow {
  label: string;
  value: string;
  confidence?: string;
}

interface ScorecardProps {
  artifact: Artifact;
}

export function Scorecard({ artifact }: ScorecardProps) {
  const rows = (artifact.data?.rows ?? []) as ScorecardRow[];

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Scorecard</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>
      <div className="mt-4 space-y-3">
        {rows.map((row) => (
          <div className="rounded-[20px] border border-ink/8 bg-white/75 px-4 py-3" key={row.label}>
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm font-medium">{row.label}</span>
              <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-accent">
                {row.value}
              </span>
            </div>
            {row.confidence ? (
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-ink/45">
                Confidence {row.confidence}
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </Card>
  );
}

