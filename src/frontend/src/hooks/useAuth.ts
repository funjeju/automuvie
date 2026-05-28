"use client";

import { useEffect, useState } from "react";
import { isFirebaseEnabled, signInWithGoogle, signOutAndClear, watchAuth } from "@/lib/firebase";

export interface AuthState {
  uid: string | null;
  enabled: boolean;
  loading: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    uid: null,
    enabled: false,
    loading: true,
  });

  useEffect(() => {
    const enabled = isFirebaseEnabled();
    if (!enabled) {
      const devUid = process.env.NEXT_PUBLIC_DEV_UID || "dev_user";
      setState({ uid: devUid, enabled: false, loading: false });
      return;
    }
    const unsub = watchAuth((uid) => {
      setState({ uid, enabled: true, loading: false });
    });
    return () => unsub();
  }, []);

  return {
    ...state,
    signIn: async () => {
      try {
        await signInWithGoogle();
      } catch (e) {
        console.error("sign-in failed", e);
      }
    },
    signOut: async () => {
      await signOutAndClear();
    },
  };
}
