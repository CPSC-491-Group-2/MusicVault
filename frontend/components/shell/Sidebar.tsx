import Link from "next/link";

import LogoMark from "@/components/brand/LogoMark";
import Wordmark from "@/components/brand/Wordmark";
import type { User } from "@/types/api";

import { SidebarAccount } from "./AccountControls";
import { NavLinks } from "./NavLinks";

const ASIDE = [
  "hidden min-[860px]:flex sticky top-0 h-dvh flex-col gap-8 overflow-y-auto border-r border-olive/14 bg-canvas px-5 py-7",
  "transition-[padding] duration-[250ms] ease-mv",
  // Collapsed content is short, and the tooltips have to leave the box.
  "group-data-[collapsed]/shell:overflow-visible group-data-[collapsed]/shell:px-3",
].join(" ");

const BRAND_FADE = "transition-[opacity] duration-200 ease-mv";

export function Sidebar({ user }: { user: User }) {
  return (
    <aside id="app-sidebar" className={ASIDE}>
      <Link
        href="/dashboard"
        className="relative flex h-[26px] w-full items-center overflow-hidden focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
      >
        <Wordmark
          theme="light"
          className={`h-[26px] w-auto shrink-0 ${BRAND_FADE} group-data-[collapsed]/shell:opacity-0`}
        />
        <LogoMark
          color="green"
          className={`absolute left-1/2 h-[26px] w-auto -translate-x-1/2 opacity-0 ${BRAND_FADE} group-data-[collapsed]/shell:opacity-100`}
        />
      </Link>

      <nav aria-label="Main">
        <NavLinks variant="sidebar" />
      </nav>

      <SidebarAccount user={user} className="mt-auto" />
    </aside>
  );
}
