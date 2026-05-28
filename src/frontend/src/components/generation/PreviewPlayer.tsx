import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";

export function PreviewPlayer({ previewUrl, audioUrl }: { previewUrl: string | null; audioUrl: string | null }) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Preview</CardTitle>
        <span className="text-xs text-muted">9:16 · 1080×1920</span>
      </CardHeader>
      <CardContent>
        <div className="relative mx-auto aspect-[9/16] w-full max-w-[360px] overflow-hidden rounded-card border border-border bg-black">
          {previewUrl ? (
            <video src={previewUrl} controls className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-xs text-muted">
              Render preview will appear here
            </div>
          )}
        </div>
        {audioUrl && (
          <audio src={audioUrl} controls className="mt-4 w-full">
            audio
          </audio>
        )}
      </CardContent>
    </Card>
  );
}
