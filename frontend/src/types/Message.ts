import type { Artifact } from './Artifact';

export interface Message {
  artifacts?: Artifact[];
  content: string;
  id: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

