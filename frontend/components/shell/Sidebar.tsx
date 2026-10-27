import Link from "next/link";

import Wordmark from "@/components/brand/Wordmark";
import { Button } from "@/components/ui/Button";
import { SPOTIFY_LOGIN_URL } from "@/lib/auth";

import { NavLinks } from "./NavLinks";

export function Sidebar() {
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
        {/* TODO: read from session once auth ships */}
        <div className="flex items-center gap-3">
          <div className="size-10 shrink-0 rounded-full bg-orchid" />
          <p className="text-[15px] font-medium">Spotify not connected</p>
        </div>
        <Button
          variant="quiet"
          size="sm"
          href={SPOTIFY_LOGIN_URL}
          external
          className="mt-1"
        >
          Connect
        </Button>
      </div>
    </aside>
  );
}
