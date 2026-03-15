import { useState } from 'react';

import { Card } from '@/components/UI/Card';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ConfidenceSource {
  name: string;
  url?: string;
  /** e.g. "firecrawl" | "serpapi" | "reddit" | "hackernews" | "linkedin" | "patent" */
  type: string;
  /** Display date, e.g. "2024-01-15" or "Jan 2024" */
  date: string;
  /** 0–1 relevance score */
  relevance: number;
}

export interface ConfidenceInsight {
  id: string;
  text: string;
  /** 0–100 confidence percentage */
  confidence: number;
  sources: ConfidenceSource[];
}

interface ConfidencePanelProps {
  insights: ConfidenceInsight[];
  title?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function confidenceColor(conf: number): string {
  if (conf >= 80) return 'text-emerald-600';
  if (conf >= 60) return 'text-amber-600';
  return 'text-rose-600';
}

function confidenceBarColor(conf: number): string {
  if (conf >= 80) return 'bg-emerald-500';
  if (conf >= 60) return 'bg-amber-400';
  return 'bg-rose-500';
}

function sourceIcon(type: string): string {
  const icons: Record<string, string> = {
    firecrawl: '🌐',
    serpapi: '🔍',
    reddit: '👥',
    hackernews: '📰',
    hn: '📰',
    linkedin: '💼',
    patent: '📜',
  };
  return icons[type.toLowerCase()] ?? '📄';
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function ConfidencePanel({ insights, title = 'Confidence & Sources' }: ConfidencePanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (insights.length === 0) {
    return (
      <Card>
        <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{title}</p>
        <p className="mt-6 py-8 text-center text-sm text-ink/50">No insights available</p>
      </Card>
    );
  }

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{title}</p>
      <h3 className="mt-2 text-lg font-semibold">Confidence &amp; Sources</h3>

      <div className="mt-4 space-y-3">
        {insights.map((insight) => {
          const isExpanded = expandedId === insight.id;

          return (
            <div
              key={insight.id}
              className="rounded-lg border border-ink/8 bg-white/75 p-4 transition hover:border-ink/20"
            >
              {/* Header row */}
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-ink">{insight.text}</p>

                  {/* Confidence bar */}
                  <div className="mt-2 flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-ink/10">
                      <div
                        className={`h-full rounded-full transition-all ${confidenceBarColor(insight.confidence)}`}
                        style={{ width: `${insight.confidence}%` }}
                      />
                    </div>
                    <span className={`shrink-0 text-sm font-bold ${confidenceColor(insight.confidence)}`}>
                      {insight.confidence}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Source toggle */}
              {insight.sources.length > 0 && (
                <button
                  onClick={() => setExpandedId(isExpanded ? null : insight.id)}
                  className="mt-3 text-xs font-medium text-accent hover:underline"
                  aria-expanded={isExpanded}
                >
                  {isExpanded ? '▼' : '▶'}&nbsp;
                  {insight.sources.length} source{insight.sources.length !== 1 ? 's' : ''}
                </button>
              )}

              {/* Expanded source trail */}
              {isExpanded && (
                <div className="mt-3 space-y-2 border-l-2 border-accent/30 pl-4">
                  {insight.sources.map((source, idx) => (
                    <div key={idx} className="text-sm">
                      {/* Source header */}
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span aria-hidden="true">{sourceIcon(source.type)}</span>
                        <span className="font-medium text-ink">{source.name}</span>
                        <span className="text-xs text-ink/45">({source.date})</span>
                      </div>

                      {/* Link */}
                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-6 mt-0.5 block text-xs text-accent hover:underline"
                        >
                          View source →
                        </a>
                      )}

                      {/* Relevance score */}
                      <p className="ml-6 mt-0.5 text-xs text-ink/50">
                        Relevance: {(source.relevance * 100).toFixed(0)}%
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
