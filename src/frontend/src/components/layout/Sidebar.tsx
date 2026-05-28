"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Disc3, FolderOpen, Music, Settings, Sparkles, Wand2 } from "lucide-react";
import { cn } from "@/lib/cn";

const NAV = [
  { href: "/", label: "Project", icon: Sparkles },
  { href: "/generate", label: "Generate", icon: Wand2 },
  { href: "/projects", label: "Library", icon: FolderOpen },
  { href: "/music", label: "Music", icon: Music },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden md:flex sticky top-0 h-screen w-[88px] shrink-0 flex-col items-center justify-between border-r border-border bg-card/40 py-6 backdrop-blur">
      <div className="flex flex-col items-center gap-6">
        <Link href="/" className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-gradient shadow-glow">
          <Disc3 className="h-5 w-5 text-white" />
        </Link>
        <nav className="flex flex-col gap-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname?.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "group flex h-12 w-12 flex-col items-center justify-center rounded-xl text-muted transition",
                  "hover:text-white hover:bg-white/5",
                  active && "text-white bg-brand-gradient shadow-glow"
                )}
                title={label}
              >
                <Icon className="h-5 w-5" />
              </Link>
            );
          })}
        </nav>
      </div>
      <Link
        href="/settings"
        className="flex h-12 w-12 items-center justify-center rounded-xl text-muted hover:text-white hover:bg-white/5"
      >
        <Settings className="h-5 w-5" />
      </Link>
    </aside>
  );
}
