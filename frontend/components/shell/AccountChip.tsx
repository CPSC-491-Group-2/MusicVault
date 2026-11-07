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
  collapsesWithSidebar?: boolean;
};

const ROOT_COLLAPSE =
  "transition-[padding] duration-[250ms] ease-mv group-data-[collapsed]/shell:p-1";

const ROW_COLLAPSE = [
  "transition-[gap] duration-[250ms] ease-mv",
  "group-data-[collapsed]/shell:justify-center group-data-[collapsed]/shell:gap-0",
].join(" ");

// Collapsed, these drop out of the tab order, but only once the sidebar has
// finished narrowing.
const HIDDEN = [
  "transition-[opacity,visibility] duration-[200ms,0s] ease-mv",
  "group-data-[collapsed]/shell:invisible group-data-[collapsed]/shell:opacity-0",
  "group-data-[collapsed]/shell:delay-[0s,250ms]",
].join(" ");

export function AccountChip({
  user,
  onLogOut,
  className,
  collapsesWithSidebar,
}: AccountChipProps) {
  const nameSource = user.display_name || user.email;
  const name = nameSource || "Your account";
  const initial = nameSource
    ? Array.from(nameSource)[0].toUpperCase()
    : undefined;
  const hidden = collapsesWithSidebar ? HIDDEN : undefined;

  return (
    <div
      className={[
        "flex flex-col items-start gap-2 rounded-2xl bg-paper p-4",
        collapsesWithSidebar ? ROOT_COLLAPSE : undefined,
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div
        className={[
          "flex w-full min-w-0 items-center gap-3",
          collapsesWithSidebar ? ROW_COLLAPSE : undefined,
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <Avatar size={40} initial={initial} />
        <p
          className={["min-w-0 truncate text-[15px] font-medium", hidden]
            .filter(Boolean)
            .join(" ")}
        >
          {name}
        </p>
      </div>
      <div
        className={["flex flex-col items-start gap-2", hidden]
          .filter(Boolean)
          .join(" ")}
      >
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
    </div>
  );
}
