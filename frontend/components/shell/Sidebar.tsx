import Link from "next/link";

import Wordmark from "@/components/brand/Wordmark";
import type { User } from "@/types/api";

import { SidebarAccount } from "./AccountControls";
import { NavLinks } from "./NavLinks";

export function Sidebar({ user }: { user: User }) {
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

      <SidebarAccount user={user} className="mt-auto" />
    </aside>
  );
}
