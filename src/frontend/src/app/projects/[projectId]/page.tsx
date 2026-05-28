"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Download, RotateCcw, XCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { AssetPanel } from "@/components/generation/AssetPanel";
import { LyricsPanel } from "@/components/generation/LyricsPanel";
import { PreviewPlayer } from "@/components/generation/PreviewPlayer";
import { TimelineStrip } from "@/components/generation/TimelineStrip";
import { WorkflowStepper } from "@/components/workflow/WorkflowStepper";
import { STATUS_LABEL } from "@/constants/workflow";
import { projectApi } from "@/services/api";
import type { ProjectDetail, RenderStatus } from "@/types/project";

const POLL_INTERVAL = 2500;

export default function ProjectDetailPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params.projectId;
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [status, setStatus] = useState<RenderStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [restarting, setRestarting] = useState(false);

  const load = useCallback(async () => {
    try {
      const [p, s] = await Promise.all([projectApi.get(projectId), projectApi.status(projectId)]);
      setProject(p);
      setStatus(s);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "프로젝트 조회 실패");
    }
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!status) return;
    if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") return;
    const handle = setInterval(load, POLL_INTERVAL);
    return () => clearInterval(handle);
  }, [load, status]);

  const onRestart = async () => {
    setRestarting(true);
    try {
      await projectApi.restart(projectId, "generating_lyrics");
      await load();
    } finally {
      setRestarting(false);
    }
  };

  const onCancel = async () => {
    try {
      await projectApi.cancel(projectId);
      await load();
    } catch (e) {
      console.error(e);
    }
  };

  const inProgress =
    status?.status &&
    !["completed", "failed", "cancelled"].includes(status.status);

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-error">{error}</p>
          <Button onClick={load} variant="secondary">
            다시 시도
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!project || !status) {
    return <p className="text-sm text-muted">Loading...</p>;
  }

  const isDone = status.status === "completed";
  const isFailed = status.status === "failed";

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wider text-muted">Project</p>
          <h1 className="text-2xl font-semibold">{project.projectId}</h1>
          <p className="mt-1 text-sm text-muted">
            {project.genre} · {project.mood} · {project.duration}s
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {inProgress && (
            <Button variant="ghost" size="sm" onClick={onCancel}>
              <XCircle className="h-4 w-4" /> 취소
            </Button>
          )}
          {isFailed && (
            <Button variant="secondary" onClick={onRestart} disabled={restarting}>
              <RotateCcw className="h-4 w-4" /> 다시 생성
            </Button>
          )}
          {project.finalVideoUrl && (
            <a href={project.finalVideoUrl} target="_blank" rel="noreferrer">
              <Button>
                <Download className="h-4 w-4" /> Final MP4
              </Button>
            </a>
          )}
        </div>
      </div>

      <WorkflowStepper status={status.status} />

      <Card>
        <CardHeader>
          <CardTitle>{STATUS_LABEL[status.status]}</CardTitle>
          <span className="text-xs text-muted">{status.progress}%</span>
        </CardHeader>
        <CardContent>
          <ProgressBar value={status.progress} />
          {status.currentStep && (
            <p className="text-xs text-muted">step: {status.currentStep}</p>
          )}
          {isFailed && (
            <p className="text-sm text-error">{project.errorMessage ?? "생성 중 문제가 발생했습니다."}</p>
          )}
          {isDone && <p className="text-sm text-success">Render complete — preview and download below.</p>}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-[1fr_360px_320px]">
        <LyricsPanel lyrics={project.lyrics} />
        <PreviewPlayer previewUrl={project.previewUrl} audioUrl={project.audioUrl} />
        <AssetPanel images={project.images} clips={project.clips} />
      </div>

      <TimelineStrip timeline={project.timeline} />
    </div>
  );
}
