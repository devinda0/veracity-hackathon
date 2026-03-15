import type { Artifact } from '@/types';

import { Card } from '@/components/UI/Card';

interface ComparisonTableProps {
  artifact: Artifact;
}

export function ComparisonTable({ artifact }: ComparisonTableProps) {
  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.kind}</p>
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
            {artifact.rows?.map((row) => (
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

