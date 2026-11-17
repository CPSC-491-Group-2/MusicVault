"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

import { isAuthErrorCode } from "@/components/auth/authErrors";
import { disconnectSpotify } from "@/lib/auth";
import type { AuthErrorCode, User } from "@/types/api";

import { SpotifyConnectionPanel } from "./SpotifyConnectionPanel";

const DISCONNECT_CONFIRM =
  "Disconnect Spotify? You can connect it again from this page.";

export function SpotifySection({
  user,
  spotify,
  error: queryError,
}: {
  user: User;
  spotify?: string;
  error?: string;
}) {
  const router = useRouter();
  const [justConnected, setJustConnected] = useState(spotify === "connected");
  const [error, setError] = useState<AuthErrorCode | undefined>(
    queryError && isAuthErrorCode(queryError) ? queryError : undefined,
  );
  const [pending, setPending] = useState(false);
  const [refreshing, startRefresh] = useTransition();

  // the message lives in state, so dropping the query keeps it on screen
  const hasQuery = spotify !== undefined || queryError !== undefined;
  useEffect(() => {
    if (hasQuery) router.replace("/profile");
  }, [hasQuery, router]);

  async function handleDisconnect() {
    if (!window.confirm(DISCONNECT_CONFIRM)) return;

    setPending(true);
    setJustConnected(false);
    setError(undefined);

    const result = await disconnectSpotify();

    if (result.ok) {
      setPending(false);
      startRefresh(() => router.refresh());
      return;
    }

    if (result.error === "session_revoked" || result.error === "unauthorized") {
      router.replace("/login");
      return;
    }

    setError(result.error);
    setPending(false);
  }

  return (
    <SpotifyConnectionPanel
      user={user}
      error={error}
      justConnected={justConnected}
      pending={pending || refreshing}
      onDisconnect={handleDisconnect}
    />
  );
}
