import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { cn } from "@/lib/cn";
import type { Lyrics } from "@/types/project";

export function LyricsPanel({ lyrics }: { lyrics: Lyrics | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Lyrics</CardTitle>
        <span className="text-xs text-muted">Verse · Chorus · Bridge</span>
      </CardHeader>
      <CardContent>
        {!lyrics && <p className="text-sm text-muted">Lyrics generating...</p>}
        {lyrics?.sections.map((section) => (
          <div
            key={section.sectionId}
            className={cn(
              "rounded-chip border border-border p-3 transition hover:border-primary/40",
              section.type === "chorus" && "bg-white/5"
            )}
          >
            <div className="mb-1 flex items-center gap-2">
              <span className="chip uppercase">{section.type}</span>
              <span className="text-xs text-muted">order {section.order}</span>
            </div>
            <p className="text-sm leading-relaxed">{section.text}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
