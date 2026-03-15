import { create } from 'zustand';

type ActivePanel = 'artifacts' | 'status' | 'context';
type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

interface UiStore {
  activeModal: string | null;
  activePanel: ActivePanel;
  sidebarOpen: boolean;
  connectionStatus: ConnectionStatus;
  setActiveModal: (value: string | null) => void;
  setActivePanel: (panel: ActivePanel) => void;
  toggleSidebar: () => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  activeModal: null,
  activePanel: 'artifacts',
  sidebarOpen: true,
  connectionStatus: 'disconnected',
  setActiveModal: (value) => set({ activeModal: value }),
  setActivePanel: (panel) => set({ activePanel: panel }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
}));

