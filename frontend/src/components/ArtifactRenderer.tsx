import type { Artifact } from '@/stores/chatStore';

import { ComparisonTable } from '@/components/Artifacts/ComparisonTable';
import { HeatMap } from '@/components/Artifacts/HeatMap';
import { Scorecard } from '@/components/Artifacts/Scorecard';
import { Timeline } from '@/components/Artifacts/Timeline';
import { TrendMap } from '@/components/Artifacts/TrendMap';
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

  switch (artifact.type) {
    case 'scorecard':
      return <Scorecard artifact={artifact} />;

    case 'trendmap':
    case 'trend-map':
      return <TrendMap artifact={artifact} />;

    case 'timeline':
      return <Timeline artifact={artifact} />;

    case 'heatmap':
    case 'heat-map':
      return <HeatMap artifact={artifact} />;

    case 'comparison':
    case 'comparison-table':
      return <ComparisonTable artifact={artifact} />;

    default:
      return (
        <Card>
          <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
          <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>
          <p className="mt-3 text-sm text-ink/70">
            Renderer for <span className="font-mono">{artifact.type}</span> is not yet available.
          </p>
        </Card>
      );
  }
}

