"use client";

import { useState } from "react";
import { ImageIcon, Film } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { cn } from "@/lib/cn";
import type { SectionClips, SectionImages } from "@/types/project";

type Tab = "image" | "video";

interface AssetPanelProps {
  images: SectionImages[];
  clips: SectionClips[];
}

export function AssetPanel({ images, clips }: AssetPanelProps) {
  const [tab, setTab] = useState<Tab>("image");

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Assets</CardTitle>
        <div className="flex items-center gap-1 rounded-chip border border-border p-1">
          <button
            type="button"
            onClick={() => setTab("image")}
            className={cn(
              "flex items-center gap-1 rounded-md px-2 py-1 text-xs transition",
              tab === "image" ? "bg-brand-gradient text-white shadow-glow" : "text-muted"
            )}
          >
            <ImageIcon className="h-3.5 w-3.5" /> Images
          </button>
          <button
            type="button"
            onClick={() => setTab("video")}
            className={cn(
              "flex items-center gap-1 rounded-md px-2 py-1 text-xs transition",
              tab === "video" ? "bg-brand-gradient text-white shadow-glow" : "text-muted"
            )}
          >
            <Film className="h-3.5 w-3.5" /> Clips
          </button>
        </div>
      </CardHeader>
      <CardContent>
        {tab === "image" ? <ImageGrid sections={images} /> : <ClipGrid sections={clips} />}
      </CardContent>
    </Card>
  );
}

function ImageGrid({ sections }: { sections: SectionImages[] }) {
  if (!sections.length) {
    return <SkeletonGrid label="이미지 생성 중..." />;
  }
  return (
    <div className="space-y-4">
      {sections.map((s) => (
        <div key={s.sectionId}>
          <p className="mb-2 text-[11px] uppercase tracking-wider text-muted">{s.sectionId}</p>
          <div className="grid grid-cols-2 gap-2">
            {s.images.map((url, i) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={`${s.sectionId}-${i}`}
                src={url}
                alt={`${s.sectionId} ${i + 1}`}
                className="aspect-[9/16] w-full rounded-md border border-border object-cover transition hover:border-primary/50"
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function ClipGrid({ sections }: { sections: SectionClips[] }) {
  if (!sections.length) {
    return <SkeletonGrid label="클립 생성 중..." />;
  }
  return (
    <div className="space-y-4">
      {sections.map((s) => (
        <div key={s.sectionId}>
          <p className="mb-2 text-[11px] uppercase tracking-wider text-muted">{s.sectionId}</p>
          <div className="grid grid-cols-2 gap-2">
            {s.clips.map((c, i) => (
              <div key={`${s.sectionId}-${i}`} className="overflow-hidden rounded-md border border-border">
                <video src={c.url} muted loop playsInline preload="metadata" className="h-full w-full object-cover" />
                <div className="p-1.5 text-[10px] text-muted">{c.duration.toFixed(1)}s</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function SkeletonGrid({ label }: { label: string }) {
  return (
    <div>
      <p className="mb-2 text-xs text-muted">{label}</p>
      <div className="grid grid-cols-2 gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="aspect-[9/16] w-full animate-pulse rounded-md border border-border bg-white/5"
          />
        ))}
      </div>
    </div>
  );
}
