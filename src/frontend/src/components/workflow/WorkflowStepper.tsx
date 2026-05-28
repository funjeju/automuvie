import { Check, Loader2 } from "lucide-react";
import { WORKFLOW_STEPS } from "@/constants/workflow";
import type { ProjectStatus } from "@/types/project";
import { cn } from "@/lib/cn";

const ORDER: ProjectStatus[] = [
  "generating_lyrics",
  "generating_music",
  "generating_images",
  "generating_video",
  "generating_subtitle",
  "rendering",
];

function indexOfStatus(status: ProjectStatus) {
  if (status === "completed") return ORDER.length;
  return ORDER.indexOf(status);
}

export function WorkflowStepper({ status }: { status: ProjectStatus }) {
  const activeIdx = indexOfStatus(status);
  return (
    <div className="panel flex items-center gap-2 overflow-x-auto p-4">
      {WORKFLOW_STEPS.map((step, i) => {
        const done = i < activeIdx;
        const active = i === activeIdx;
        return (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={cn(
                "flex h-9 min-w-[120px] items-center justify-center gap-2 rounded-chip border px-3 text-xs transition",
                done && "border-success/30 bg-success/10 text-success",
                active && "border-transparent bg-brand-gradient text-white shadow-glow",
                !done && !active && "border-border text-muted"
              )}
            >
              {done ? (
                <Check className="h-4 w-4" />
              ) : active ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <span className="text-[10px] opacity-60">{i + 1}</span>
              )}
              {step.label}
            </div>
            {i < WORKFLOW_STEPS.length - 1 && (
              <div className={cn("h-px w-6 bg-border", done && "bg-success/40")} />
            )}
          </div>
        );
      })}
    </div>
  );
}
