"use client";

import { useEffect, useState } from "react";

import { Button, type ButtonSize } from "@/components/ui/Button";
import { LoadingStack } from "@/components/ui/LoadingStack";
import { SPOTIFY_LOGIN_URL } from "@/lib/auth";

type SpotifyContinueButtonProps = {
  size: ButtonSize;
  href?: string;
  className?: string;
};

// external: the login URL is an /api proxy route to Flask, not a page, so a
// next Link would prefetch it and start a real OAuth handshake on scroll.
export function SpotifyContinueButton({
  size,
  href = SPOTIFY_LOGIN_URL,
  className,
}: SpotifyContinueButtonProps) {
  const [pending, setPending] = useState(false);

  // a page restored from the back/forward cache comes back still pending.
  useEffect(() => {
    const onPageShow = (event: PageTransitionEvent) => {
      if (event.persisted) {
        setPending(false);
      }
    };

    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, []);

  return (
    <Button
      variant="secondary"
      size={size}
      href={href}
      external
      className={className}
      onClick={(event) => {
        if (pending) {
          event.preventDefault();
          return;
        }
        setPending(true);
      }}
      aria-busy={pending || undefined}
      aria-disabled={pending || undefined}
    >
      {pending ? (
        <>
          <LoadingStack size={22} mono label="" />
          <span>Opening Spotify</span>
        </>
      ) : (
        "Continue with Spotify"
      )}
    </Button>
  );
}
