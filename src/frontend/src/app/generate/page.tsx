"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Chip } from "@/components/ui/Chip";
import { Input, Label, Textarea } from "@/components/ui/Input";
import { GENRE_OPTIONS, MOOD_OPTIONS } from "@/constants/workflow";
import { projectApi } from "@/services/api";

const DRAFT_KEY = "automuvie_generate_draft";

interface Draft {
  genre: string;
  mood: string;
  prompt: string;
  duration: number;
}

export default function GeneratePage() {
  const router = useRouter();
  const [genre, setGenre] = useState<string>(GENRE_OPTIONS[0]);
  const [mood, setMood] = useState<string>(MOOD_OPTIONS[0]);
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState(120);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  // Restore draft on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        const d: Draft = JSON.parse(raw);
        if (GENRE_OPTIONS.includes(d.genre)) setGenre(d.genre);
        if (MOOD_OPTIONS.includes(d.mood)) setMood(d.mood);
        if (d.prompt) setPrompt(d.prompt);
        if (d.duration >= 60 && d.duration <= 180) setDuration(d.duration);
      }
    } catch {}
  }, []);

  const saveDraft = () => {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ genre, mood, prompt, duration }));
    setSaved(true);
    setTimeout(() => setSaved(false), 1800);
  };

  const submit = async () => {
    setError(null);
    if (duration < 60 || duration > 180) {
      setError("Duration은 60~180초 사이여야 합니다.");
      return;
    }
    setLoading(true);
    try {
      const res = await projectApi.create({ genre, mood, prompt, duration });
      localStorage.removeItem(DRAFT_KEY);
      router.push(`/projects/${res.projectId}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "프로젝트 생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>New Music Video</CardTitle>
          <span className="text-xs text-muted">장르 · 분위기 · 프롬프트 입력</span>
        </CardHeader>
        <CardContent>
          <div>
            <Label>Genre</Label>
            <div className="flex flex-wrap gap-2">
              {GENRE_OPTIONS.map((g) => (
                <Chip key={g} active={genre === g} onClick={() => setGenre(g)}>
                  {g}
                </Chip>
              ))}
            </div>
          </div>

          <div>
            <Label>Mood</Label>
            <div className="flex flex-wrap gap-2">
              {MOOD_OPTIONS.map((m) => (
                <Chip key={m} active={mood === m} onClick={() => setMood(m)}>
                  {m}
                </Chip>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="prompt">Prompt (선택)</Label>
            <Textarea
              id="prompt"
              maxLength={500}
              placeholder="e.g. 비 오는 도시의 따뜻한 기억"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <p className="mt-1 text-right text-[11px] text-muted">{prompt.length}/500</p>
          </div>

          <div>
            <Label htmlFor="duration">Duration (60-180s)</Label>
            <div className="flex items-center gap-3">
              <Input
                id="duration"
                type="number"
                min={60}
                max={180}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="max-w-[140px]"
              />
              <input
                type="range"
                min={60}
                max={180}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="flex-1 accent-[#B14CFF]"
              />
            </div>
          </div>

          {error && <p className="text-sm text-error">{error}</p>}

          <div className="flex flex-wrap items-center gap-3">
            <Button size="lg" onClick={submit} disabled={loading} className="w-full md:w-auto">
              {loading ? "생성 중..." : "생성 시작"}
            </Button>
            <Button variant="secondary" size="sm" onClick={saveDraft} disabled={loading}>
              <Save className="h-4 w-4" />
              {saved ? "저장됨" : "임시 저장"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2 text-sm text-muted">
            <li>1. Claude로 가사 생성</li>
            <li>2. Lyria 3 Pro로 음악 생성</li>
            <li>3. GPT Image로 section별 이미지 생성</li>
            <li>4. Veo 3.1로 클립 생성</li>
            <li>5. Whisper로 가사 싱크 추출</li>
            <li>6. ffmpeg로 최종 합성</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
