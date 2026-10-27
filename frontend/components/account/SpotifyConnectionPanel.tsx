"use client";

import { useId } from "react";

import { authErrorMessage } from "@/components/auth/authErrors";
import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/FormMessage";
import { Surface } from "@/components/ui/Surface";
import { SPOTIFY_CONNECT_URL } from "@/lib/auth";
import type { AuthErrorCode, User } from "@/types/api";

type SpotifyConnectionPanelProps = {
  user: User;
  error?: AuthErrorCode;
  justConnected?: boolean;
  pending?: boolean;
  onDisconnect?: () => void;
  className?: string;
};

export function SpotifyConnectionPanel({
  user,
  error,
  justConnected = false,
  pending = false,
  onDisconnect,
  className,
}: SpotifyConnectionPanelProps) {
  const hintId = useId();

  return (
    <Surface
      className={["flex flex-col gap-5", className].filter(Boolean).join(" ")}
    >
      <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
        Spotify
      </h2>

      {justConnected ? (
        <FormMessage tone="success">
          Spotify connected. Your top songs are on the way.
        </FormMessage>
      ) : null}
      {error ? (
        <FormMessage tone="error">{authErrorMessage(error)}</FormMessage>
      ) : null}

      {user.spotify.connected ? (
        <>
          <p className="max-w-[60ch] text-[17px] leading-[1.5]">
            {user.spotify.display_name
              ? `Connected as ${user.spotify.display_name}`
              : "Spotify connected"}
          </p>
          <div className="flex flex-col items-start gap-3">
            <Button
              variant="secondary"
              size="md"
              disabled={!user.has_password || pending}
              aria-busy={pending || undefined}
              aria-describedby={user.has_password ? undefined : hintId}
              onClick={onDisconnect}
            >
              {pending ? "Disconnecting" : "Disconnect Spotify"}
            </Button>
            {user.has_password ? null : (
              <p
                id={hintId}
                className="max-w-[60ch] text-[15px] leading-[1.45] text-olive/70"
              >
                Add a password first, so you can still log in after you
                disconnect.
              </p>
            )}
          </div>
        </>
      ) : (
        <>
          <p className="max-w-[60ch] text-[17px] leading-[1.5] text-olive/70">
            Connect Spotify to bring in your top songs.
          </p>
          <Button
            variant="primary"
            size="md"
            href={SPOTIFY_CONNECT_URL}
            external
            className="self-start"
          >
            Connect Spotify
          </Button>
        </>
      )}
    </Surface>
  );
}
