import type { ProjectStatus } from "@/types/project";

export const WORKFLOW_STEPS: { key: ProjectStatus; label: string }[] = [
  { key: "generating_lyrics", label: "Lyrics" },
  { key: "generating_music", label: "Music" },
  { key: "generating_images", label: "Image" },
  { key: "generating_video", label: "Video" },
  { key: "generating_subtitle", label: "Subtitle" },
  { key: "rendering", label: "Render" },
];

export const STATUS_LABEL: Record<ProjectStatus, string> = {
  queued: "Queued",
  generating_lyrics: "Lyrics generating...",
  generating_music: "Creating cinematic audio...",
  generating_images: "Painting visuals...",
  generating_video: "Animating clips...",
  generating_subtitle: "Syncing karaoke subtitle...",
  rendering: "Rendering final music video...",
  completed: "Completed",
  failed: "Failed",
  cancelled: "Cancelled",
};

export const GENRE_OPTIONS = [
  "cinematic emotional",
  "lofi chill",
  "synth pop",
  "ambient",
  "indie rock",
  "k-ballad",
] as const;

export const MOOD_OPTIONS = ["nostalgic", "energetic", "calm", "dark", "uplifting", "romantic"] as const;
