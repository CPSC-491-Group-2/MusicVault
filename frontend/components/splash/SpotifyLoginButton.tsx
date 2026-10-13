import { Button } from "@/components/ui/Button";
import { SPOTIFY_LOGIN_URL } from "@/lib/auth";

type SpotifyLoginButtonProps = {
  size: "sm" | "lg";
  className?: string;
};

// external: the login URL is an /api proxy route to Flask, not a page, so a
// next Link would prefetch it and start a real OAuth handshake on scroll.
export default function SpotifyLoginButton({
  size,
  className,
}: SpotifyLoginButtonProps) {
  return (
    <Button
      variant="primary"
      size={size}
      href={SPOTIFY_LOGIN_URL}
      external
      className={className}
    >
      Log in with Spotify
    </Button>
  );
}
