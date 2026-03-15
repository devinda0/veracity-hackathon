import type { Artifact } from '@/stores/chatStore';

import { Card } from '@/components/UI/Card';

interface ComparisonRow {
  label: string;
  value: string;
  confidence?: string;
}

interface ComparisonTableData {
  features?: string[];
  competitors?: Record<string, unknown[]>;
  rows?: ComparisonRow[];
}

interface ComparisonTableProps {
  artifact: Artifact;
}

export function ComparisonTable({ artifact }: ComparisonTableProps) {
  const data = (artifact.data ?? {}) as ComparisonTableData;
  const features = data.features ?? [];
  const competitors = data.competitors ?? {};
  const competitorNames = Object.keys(competitors);
  const rows = data.rows ?? [];

  // Feature-by-competitor matrix (Issue #37 spec format)
  if (features.length > 0 && competitorNames.length > 0) {
    return (
      <Card>
        <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
        <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr>
                <th className="border border-gray-300 bg-mist p-3 text-left font-semibold">
                  Feature
                </th>
                {competitorNames.map((competitor) => (
                  <th
                    key={competitor}
                    className="border border-gray-300 bg-mist p-3 text-center font-semibold"
                  >
                    {competitor}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map((feature, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white/75' : 'bg-mist/40'}>
                  <td className="border border-ink/8 p-3 font-medium text-ink">{feature}</td>
                  {competitorNames.map((competitor) => {
                    const vals = competitors[competitor] ?? [];
                    const present = Boolean(vals[idx]);
                    return (
                      <td
                        key={competitor}
                        className="border border-ink/8 p-3 text-center"
                      >
                        {present ? (
                          <span className="text-lg font-bold text-green-600">✓</span>
                        ) : (
                          <span className="text-lg font-bold text-ink/25">○</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    );
  }

  // Legacy rows[] fallback
  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>
      <div className="mt-4 overflow-hidden rounded-[20px] border border-ink/8">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="bg-mist">
            <tr>
              <th className="px-4 py-3 font-medium">Competitor</th>
              <th className="px-4 py-3 font-medium">Signal</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
            </tr>
          </thead>
          <tbody className="bg-white/75">
            {rows.map((row) => (
              <tr className="border-t border-ink/8" key={row.label}>
                <td className="px-4 py-3">{row.label}</td>
                <td className="px-4 py-3">{row.value}</td>
                <td className="px-4 py-3">{row.confidence ?? 'n/a'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

