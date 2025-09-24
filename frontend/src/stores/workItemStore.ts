import { create } from 'zustand';
import { WorkItem } from '@/types/workItem.types';

interface WorkItemStore {
  workItems: WorkItem[];
  setWorkItems: (workItems: WorkItem[]) => void;
  addWorkItem: (workItem: WorkItem) => void;
  updateWorkItem: (workItem: WorkItem) => void;
  removeWorkItem: (workItemId: string) => void;
}

export const useWorkItemStore = create<WorkItemStore>((set) => ({
  workItems: [],

  setWorkItems: (workItems) => set({ workItems }),

  addWorkItem: (workItem) =>
    set((state) => ({
      workItems: [...state.workItems, workItem]
    })),

  updateWorkItem: (workItem) =>
    set((state) => ({
      workItems: state.workItems.map((item) =>
        item.id === workItem.id ? workItem : item
      )
    })),

  removeWorkItem: (workItemId) =>
    set((state) => ({
      workItems: state.workItems.filter((item) => item.id !== workItemId)
    }))
}));
