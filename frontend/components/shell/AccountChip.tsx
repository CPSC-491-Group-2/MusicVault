import { LogOutButton } from "@/components/account/LogOutButton";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import { CheckIcon } from "@/components/ui/icons";
import { SPOTIFY_CONNECT_URL } from "@/lib/auth";
import type { User } from "@/types/api";

type AccountChipProps = {
  user: User;
  onLogOut?: () => void;
  className?: string;
};

export function AccountChip({ user, onLogOut, className }: AccountChipProps) {
  const nameSource = user.display_name || user.email;
  const name = nameSource || "Your account";
  const initial = nameSource
    ? Array.from(nameSource)[0].toUpperCase()
    : undefined;

  return (
    <div
      className={[
        "flex flex-col items-start gap-2 rounded-2xl bg-paper p-4",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="flex w-full min-w-0 items-center gap-3">
        <Avatar size={40} initial={initial} />
        <p className="min-w-0 truncate text-[15px] font-medium">{name}</p>
      </div>
      {user.spotify.connected ? (
        <p className="flex items-center gap-2 text-[15px] leading-[1.45] text-olive/70">
          <CheckIcon className="h-5 w-5 shrink-0 text-green" />
          Spotify connected
        </p>
      ) : (
        <Button variant="quiet" size="sm" href={SPOTIFY_CONNECT_URL} external>
          Connect Spotify
        </Button>
      )}
      <LogOutButton onLogOut={onLogOut} />
    </div>
  );
}
