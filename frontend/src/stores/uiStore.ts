import { create } from 'zustand';

type ActivePanel = 'artifacts' | 'status' | 'context';

interface UiStore {
  activeModal: string | null;
  activePanel: ActivePanel;
  sidebarOpen: boolean;
  setActiveModal: (value: string | null) => void;
  setActivePanel: (panel: ActivePanel) => void;
  toggleSidebar: () => void;
}

export const useUiStore = create<UiStore>((set) => ({
  activeModal: null,
  activePanel: 'artifacts',
  sidebarOpen: true,
  setActiveModal: (value) => set({ activeModal: value }),
  setActivePanel: (panel) => set({ activePanel: panel }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));

