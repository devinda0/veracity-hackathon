import { useMemo, useState } from 'react';

import type { Artifact } from '@/stores/chatStore';

import { Card } from '@/components/UI/Card';

interface CategoryScore {
  score: number;
  status: 'strong' | 'moderate' | 'opportunity' | 'weak' | string;
}

interface ScorecardData {
  overall_score: number;
  categories: Record<string, CategoryScore>;
  insights?: string[];
}

interface ScorecardProps {
  artifact: Artifact;
}

export function Scorecard({ artifact }: ScorecardProps) {
  const [expanded, setExpanded] = useState(false);

  const scorecardData = useMemo<ScorecardData>(() => {
    const fallbackCategories = (() => {
      const rowLike = (artifact.data?.rows ?? []) as Array<{
        label?: string;
        value?: string | number;
        confidence?: string;
      }>;

      return rowLike.reduce<Record<string, CategoryScore>>((acc, row) => {
        if (!row.label) {
          return acc;
        }

        const numericValue = Number(row.value ?? 0);
        const normalized = Number.isFinite(numericValue)
          ? Math.max(0, Math.min(100, numericValue))
          : 0;

        acc[row.label] = {
          score: normalized,
          status: normalized >= 75 ? 'strong' : normalized >= 50 ? 'moderate' : 'opportunity',
        };

        return acc;
      }, {});
    })();

    const data = artifact.data as Partial<ScorecardData>;
    const categories = data.categories && Object.keys(data.categories).length > 0 ? data.categories : fallbackCategories;

    return {
      overall_score: Number(data.overall_score ?? 0),
      categories,
      insights: Array.isArray(data.insights) ? data.insights : undefined,
    };
  }, [artifact.data]);

  const safeOverall = Math.max(0, Math.min(100, scorecardData.overall_score || 0));
  const circumference = 2 * Math.PI * 45;
  const progress = (safeOverall / 100) * circumference;

  const statusClass: Record<string, string> = {
    strong: 'bg-emerald-500',
    moderate: 'bg-amber-500',
    opportunity: 'bg-blue-500',
    weak: 'bg-rose-500',
  };

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Scorecard</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>

      <div className="mt-6 flex justify-center">
        <div className="relative h-36 w-36">
          <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="6" className="text-mist" />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="currentColor"
              strokeWidth="6"
              className="text-accent"
              strokeLinecap="round"
              strokeDasharray={`${progress} ${circumference}`}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl font-bold text-accent">{safeOverall}</div>
              <div className="text-xs uppercase tracking-[0.16em] text-ink/55">Growth score</div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {Object.entries(scorecardData.categories).map(([category, stats]) => (
          <div className="rounded-[16px] border border-ink/8 bg-white/75 p-3" key={category}>
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-medium capitalize">{category.replace(/_/g, ' ')}</div>
              <div className="text-sm font-semibold text-ink">{stats.score}</div>
            </div>
            <div className="mt-2 h-2.5 rounded-full bg-mist">
              <div
                className={`h-2.5 rounded-full ${statusClass[stats.status] ?? 'bg-slate-400'}`}
                style={{ width: `${Math.max(0, Math.min(100, stats.score))}%` }}
              />
            </div>
            <div className="mt-2 text-xs uppercase tracking-[0.16em] text-ink/55">{stats.status}</div>
          </div>
        ))}
      </div>

      <button
        onClick={() => setExpanded((value) => !value)}
        className="mt-4 text-sm font-medium text-accent transition hover:text-accent/80"
        type="button"
      >
        {expanded ? '▼ Hide insights' : '▶ Show insights'}
      </button>

      {expanded ? (
        <div className="mt-3 rounded-[16px] border border-accent/20 bg-accent/5 p-4 text-sm text-ink/75">
          {scorecardData.insights?.length ? (
            <ul className="space-y-1.5">
              {scorecardData.insights.map((insight) => (
                <li key={insight}>• {insight}</li>
              ))}
            </ul>
          ) : (
            <p>Detailed insights and recommendations appear here based on domain analysis.</p>
          )}
        </div>
      ) : null}
    </Card>
  );
}

