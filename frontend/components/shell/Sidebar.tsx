
import Link from "next/link";

import Wordmark from "@/components/brand/Wordmark";
import type { CurrentUser } from "@/types/api";

import { LogoutButton } from "./LogoutButton";
import { NavLinks } from "./NavLinks";

type SidebarProps = {
  user: CurrentUser;
};

export function Sidebar({ user }: SidebarProps) {
  const accountName =
    user.display_name ??
    user.spotify.display_name ??
    user.email ??
    "MusicVault User";

  return (
    <aside className="hidden min-[860px]:flex sticky top-0 h-dvh flex-col gap-8 overflow-y-auto border-r border-olive/14 bg-canvas px-5 py-7">
      <Link
        href="/dashboard"
        className="focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
      >
        <Wordmark theme="light" className="h-[26px] w-auto" />
      </Link>

      <nav aria-label="Main">
        <NavLinks variant="sidebar" />
      </nav>

      <div className="mt-auto rounded-2xl bg-paper p-4">
        <div className="flex items-center gap-3">
          <div className="size-10 shrink-0 rounded-full bg-orchid" />

          <div className="min-w-0">
            <p className="truncate text-[15px] font-medium">
              {accountName}
            </p>

            <p className="text-sm text-olive/70">
              {user.spotify.connected
                ? "Spotify connected"
                : "Spotify not connected"}
            </p>
          </div>
        </div>

        {user.email && user.email !== accountName && (
          <p className="mt-3 truncate text-sm text-olive/70">
            {user.email}
          </p>
        )}

        <div className="mt-4 border-t border-olive/14 pt-4">
          <LogoutButton />
        </div>
      </div>
    </aside>
  );
}
