export type ProjectStatus =
  | "queued"
  | "generating_lyrics"
  | "generating_music"
  | "generating_images"
  | "generating_video"
  | "generating_subtitle"
  | "rendering"
  | "completed"
  | "failed"
  | "cancelled";

export interface LyricSection {
  sectionId: string;
  type: "verse" | "chorus" | "bridge";
  order: number;
  text: string;
}

export interface Lyrics {
  sections: LyricSection[];
}

export interface SectionImages {
  sectionId: string;
  images: string[];
}

export interface VideoClipMeta {
  url: string;
  duration: number;
}

export interface SectionClips {
  sectionId: string;
  clips: VideoClipMeta[];
}

export interface TimelineSegment {
  sectionId: string;
  start: number;
  end: number;
}

export interface ProjectDetail {
  projectId: string;
  uid: string;
  genre: string;
  mood: string;
  prompt: string;
  duration: number;
  status: ProjectStatus;
  progress: number;
  lyrics: Lyrics | null;
  audioUrl: string | null;
  subtitleUrl: string | null;
  previewUrl: string | null;
  finalVideoUrl: string | null;
  images: SectionImages[];
  clips: SectionClips[];
  timeline: TimelineSegment[];
  errorCode: string | null;
  errorMessage: string | null;
  retryCount: number;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface ProjectListItem {
  projectId: string;
  genre: string;
  mood: string;
  duration: number;
  status: ProjectStatus;
  progress: number;
  previewUrl: string | null;
  finalVideoUrl: string | null;
  createdAt: string | null;
}

export interface RenderStatus {
  projectId: string;
  status: ProjectStatus;
  progress: number;
  currentStep: string;
  errorCode: string | null;
  errorMessage: string | null;
}

export interface CreateProjectRequest {
  genre: string;
  mood: string;
  prompt: string;
  duration: number;
  language: string;
  style: string;
}

export interface ApiSuccess<T> {
  success: true;
  data: T;
  message?: string;
}

export interface ApiError {
  success: false;
  error: { code: string; message: string };
}

export type ApiResponse<T> = ApiSuccess<T> | ApiError;
