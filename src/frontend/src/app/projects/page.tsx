"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { STATUS_LABEL } from "@/constants/workflow";
import { projectApi } from "@/services/api";
import type { ProjectListItem } from "@/types/project";

export default function ProjectListPage() {
  const [items, setItems] = useState<ProjectListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await projectApi.list();
        setItems(res.items);
      } catch (e) {
        setError(e instanceof Error ? e.message : "조회 실패");
      }
    })();
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">My Projects</h1>
        <Link href="/generate">
          <Button>
            <Plus className="h-4 w-4" /> 새 프로젝트
          </Button>
        </Link>
      </div>

      {error && (
        <Card>
          <p className="text-sm text-error">{error}</p>
        </Card>
      )}

      {!items && !error && <p className="text-sm text-muted">Loading...</p>}

      {items && items.length === 0 && (
        <Card>
          <p className="text-sm text-muted">아직 프로젝트가 없습니다. 시작해보세요.</p>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items?.map((p) => (
          <Link key={p.projectId} href={`/projects/${p.projectId}`}>
            <Card className="cursor-pointer transition hover:border-primary/40 hover:shadow-glow">
              <div className="aspect-[9/16] w-full overflow-hidden rounded-md border border-border bg-black">
                {p.previewUrl ? (
                  <video src={p.previewUrl} muted className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-xs text-muted">
                    {STATUS_LABEL[p.status]}
                  </div>
                )}
              </div>
              <div className="mt-3 space-y-1">
                <p className="truncate text-sm font-medium">{p.projectId}</p>
                <p className="text-xs text-muted">
                  {p.genre} · {p.mood} · {p.duration}s
                </p>
                <ProgressBar value={p.progress} />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
