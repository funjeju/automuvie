"use client";

import { LogIn, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

export function AccountButton() {
  const { uid, enabled, loading, signIn, signOut } = useAuth();
  if (loading) return null;

  if (!enabled) {
    return (
      <div className="flex items-center gap-2 rounded-chip border border-border px-3 py-1.5 text-xs text-muted">
        <User className="h-3.5 w-3.5" />
        dev:{uid}
      </div>
    );
  }

  if (uid) {
    return (
      <Button variant="ghost" size="sm" onClick={signOut}>
        <LogOut className="h-3.5 w-3.5" /> 로그아웃
      </Button>
    );
  }

  return (
    <Button variant="secondary" size="sm" onClick={signIn}>
      <LogIn className="h-3.5 w-3.5" /> 구글로 시작
    </Button>
  );
}
