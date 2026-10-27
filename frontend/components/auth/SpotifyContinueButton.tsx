import { Button, type ButtonSize } from "@/components/ui/Button";
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
  return (
    <Button
      variant="secondary"
      size={size}
      href={href}
      external
      className={className}
    >
      Continue with Spotify
    </Button>
  );
}
