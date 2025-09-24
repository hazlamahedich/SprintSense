export interface Dependency {
  id: string;
  source: {
    id: string;
    title: string;
  };
  target: {
    id: string;
    title: string;
  };
  type: DependencyType;
  isCritical: boolean;
  confidence: number;
  createdAt: string;
  updatedAt: string;
}

export enum DependencyType {
  BLOCKS = 'blocks',
  DEPENDS_ON = 'depends_on',
  RELATES_TO = 'relates_to'
}

export interface DependencyAnalysisResult {
  dependencies: Dependency[];
  criticalPath: string[];
  suggestedChain: WorkItem[];
  confidence: number;
}

export interface WorkItem {
  id: string;
  title: string;
  description: string;
  status: WorkItemStatus;
  priority: number;
  dependencies?: Dependency[];
  estimatedTime?: number;
  assignee?: string;
  createdAt: string;
  updatedAt: string;
}

export enum WorkItemStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  BLOCKED = 'blocked',
  COMPLETED = 'completed'
}
