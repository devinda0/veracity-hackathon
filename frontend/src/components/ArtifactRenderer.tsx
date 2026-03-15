import type { Artifact } from '@/stores/chatStore';

import { ComparisonTable } from '@/components/Artifacts/ComparisonTable';
import { Scorecard } from '@/components/Artifacts/Scorecard';
import { Card } from '@/components/UI/Card';

interface ArtifactRendererProps {
  artifact?: Artifact;
}

export function ArtifactRenderer({ artifact }: ArtifactRendererProps) {
  if (!artifact) {
    return (
      <Card className="min-h-[280px]">
        <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Artifacts</p>
        <h3 className="mt-2 font-display text-2xl">Nothing rendered yet</h3>
        <p className="mt-3 text-sm text-ink/70">
          Artifact cards from the synthesis pipeline will appear here once backend orchestration and
          streaming are connected.
        </p>
      </Card>
    );
  }

  if (artifact.type === 'scorecard') {
    return <Scorecard artifact={artifact} />;
  }

  return <ComparisonTable artifact={artifact} />;
}

