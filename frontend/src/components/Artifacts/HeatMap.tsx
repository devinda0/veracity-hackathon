import { useState } from 'react';

import type { Artifact } from '@/stores/chatStore';
import { Card } from '@/components/UI/Card';

interface HeatMapData {
  dimensions?: string[];
  competitors?: Record<string, number[]>;
}

interface HeatMapProps {
  artifact: Artifact;
}

function getColor(score: number): string {
  if (score >= 8) return 'bg-green-500';
  if (score >= 6) return 'bg-yellow-400';
  if (score >= 4) return 'bg-orange-400';
  return 'bg-red-400';
}

export function HeatMap({ artifact }: HeatMapProps) {
  const [hoveredCell, setHoveredCell] = useState<string | null>(null);

  const data = (artifact.data ?? {}) as HeatMapData;
  const dimensions = data.dimensions ?? [];
  const competitors = data.competitors ?? {};
  const competitorNames = Object.keys(competitors);

  if (dimensions.length === 0 || competitorNames.length === 0) {
    return (
      <Card>
        <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
        <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>
        <p className="mt-6 py-8 text-center text-sm text-ink/50">
          No heat-map data available
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="border border-gray-300 bg-mist p-2 text-left font-semibold">
                Dimension
              </th>
              {competitorNames.map((competitor) => (
                <th
                  key={competitor}
                  className="border border-gray-300 bg-mist p-2 text-center font-semibold"
                >
                  {competitor}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dimensions.map((dim, dimIdx) => (
              <tr key={dim}>
                <td className="border border-gray-300 bg-gray-50 p-2 font-medium text-ink">
                  {dim}
                </td>
                {competitorNames.map((competitor) => {
                  const scores = competitors[competitor] ?? [];
                  const score = scores[dimIdx] ?? 0;
                  const cellKey = `${competitor}-${dim}`;
                  return (
                    <td
                      key={cellKey}
                      className={`relative cursor-pointer border border-gray-300 p-3 text-center font-bold text-white transition ${getColor(score)}`}
                      onMouseEnter={() => setHoveredCell(cellKey)}
                      onMouseLeave={() => setHoveredCell(null)}
                      title={`${competitor} — ${dim}: ${score}/10`}
                    >
                      {score}
                      {hoveredCell === cellKey && (
                        <div className="mt-1 text-xs text-white">{score}/10</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-green-500" />
          <span>Strong (8–10)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-yellow-400" />
          <span>Good (6–7)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-orange-400" />
          <span>Fair (4–5)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-red-400" />
          <span>Weak (1–3)</span>
        </div>
      </div>
    </Card>
  );
}
