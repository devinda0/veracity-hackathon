export interface AgentStatus {
  id: string;
  label: string;
  state: 'idle' | 'running' | 'blocked' | 'complete';
}

