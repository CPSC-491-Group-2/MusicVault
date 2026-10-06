import { SPOTIFY_LOGIN_URL } from "@/lib/auth";

type SpotifyLoginButtonProps = {
  size: "sm" | "lg";
  className?: string;
};

const SIZE_CLASSES: Record<SpotifyLoginButtonProps["size"], string> = {
  sm: "text-base px-5 py-[11px] rounded-[10px]",
  lg: "text-lg px-7 py-[17px] rounded-xl",
};

export default function SpotifyLoginButton({
  size,
  className,
}: SpotifyLoginButtonProps) {
  return (
    <a
      href={SPOTIFY_LOGIN_URL}
      className={[
        "inline-block bg-olive text-blush font-medium",
        "hover:bg-green focus-visible:bg-green",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
        SIZE_CLASSES[size],
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      Log in with Spotify
    </a>
  );
}
