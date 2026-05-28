import { create } from "zustand";
import type { ProjectDetail, RenderStatus } from "@/types/project";

interface State {
  project: ProjectDetail | null;
  status: RenderStatus | null;
  setProject: (p: ProjectDetail | null) => void;
  setStatus: (s: RenderStatus | null) => void;
}

export const useProjectStore = create<State>((set) => ({
  project: null,
  status: null,
  setProject: (project) => set({ project }),
  setStatus: (status) => set({ status }),
}));
