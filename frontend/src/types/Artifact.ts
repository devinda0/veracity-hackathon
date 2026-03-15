export interface ArtifactRow {
  confidence?: string;
  label: string;
  value: string;
}

export interface Artifact {
  id: string;
  kind: 'scorecard' | 'comparison-table';
  rows?: ArtifactRow[];
  title: string;
}

