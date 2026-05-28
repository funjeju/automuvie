import Link from "next/link";
import { Sparkles } from "lucide-react";
import { AccountButton } from "./AccountButton";

export function TopBar() {
  return (
    <header className="mb-8 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-2 text-sm font-semibold">
        <Sparkles className="h-4 w-4 text-primary" />
        Vibe Creator
      </Link>
      <AccountButton />
    </header>
  );
}
