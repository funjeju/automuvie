import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import type { TimelineSegment } from "@/types/project";

const TYPE_COLOR: Record<string, string> = {
  verse: "from-violet-500 to-violet-700",
  chorus: "from-pink-500 to-fuchsia-500",
  bridge: "from-amber-500 to-orange-500",
};

function fmt(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TimelineStrip({ timeline }: { timeline: TimelineSegment[] }) {
  if (!timeline.length) return null;
  const total = timeline[timeline.length - 1]?.end ?? 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Timeline</CardTitle>
        <span className="text-xs text-muted">{fmt(total)}</span>
      </CardHeader>
      <CardContent>
        <div className="flex h-12 w-full overflow-hidden rounded-chip border border-border">
          {timeline.map((seg) => {
            const width = ((seg.end - seg.start) / total) * 100;
            const type = seg.sectionId.split("_")[0];
            const gradient = TYPE_COLOR[type] ?? TYPE_COLOR.verse;
            return (
              <div
                key={seg.sectionId}
                style={{ width: `${width}%` }}
                className={`group relative flex items-center justify-center bg-gradient-to-br ${gradient} text-[10px] uppercase tracking-wide text-white`}
                title={`${seg.sectionId} ${fmt(seg.start)} - ${fmt(seg.end)}`}
              >
                <span className="px-2 truncate opacity-90">{seg.sectionId}</span>
              </div>
            );
          })}
        </div>
        <div className="mt-2 grid grid-cols-3 text-[10px] text-muted">
          <span>0:00</span>
          <span className="text-center">{fmt(total / 2)}</span>
          <span className="text-right">{fmt(total)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
