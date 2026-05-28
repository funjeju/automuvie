import Link from "next/link";
import { Sparkles, Wand2, Music, Film } from "lucide-react";
import { Button } from "@/components/ui/Button";

const FEATURES = [
  { icon: Wand2, title: "Prompt → Lyrics", desc: "Claude-style verse · chorus · bridge generation" },
  { icon: Music, title: "AI Music", desc: "Lyria 3 Pro instrumentals with mood control" },
  { icon: Film, title: "Cinematic Clips", desc: "GPT image + Veo motion + karaoke subtitle burn" },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-5xl">
      <section className="relative overflow-hidden rounded-card border border-border bg-card/40 p-10 md:p-16">
        <div className="absolute inset-0 -z-10 bg-panel-gradient" />
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-muted">
          <Sparkles className="h-4 w-4 text-primary" /> AI Music Video Studio
        </div>
        <h1 className="mt-4 text-4xl font-bold leading-tight md:text-6xl">
          Prompt 한 줄로
          <br />
          <span className="bg-brand-gradient bg-clip-text text-transparent">시네마틱 뮤직비디오</span>를 만든다.
        </h1>
        <p className="mt-4 max-w-2xl text-muted">
          장르와 분위기를 입력하면 가사 · 음악 · 영상 · 자막까지 자동으로 합성합니다. 2~3분 안에 최종 mp4를 다운로드하세요.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/generate">
            <Button size="lg">시작하기</Button>
          </Link>
          <Link href="/projects">
            <Button size="lg" variant="secondary">
              내 프로젝트
            </Button>
          </Link>
        </div>
      </section>

      <section className="mt-10 grid gap-4 md:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="panel p-6">
            <Icon className="h-6 w-6 text-primary" />
            <h3 className="mt-3 font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-muted">{desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
