import Link from "next/link";
import type { ReactNode } from "react";

import Wordmark from "@/components/brand/Wordmark";
import type { User } from "@/types/api";

import { MobileLogOut } from "./AccountControls";
import { MobileTabBar } from "./MobileTabBar";
import { Sidebar } from "./Sidebar";

type AppShellProps = {
  user: User;
  children: ReactNode;
};

export function AppShell({ user, children }: AppShellProps) {
  return (
    <div className="min-h-dvh bg-canvas min-[860px]:grid min-[860px]:grid-cols-[260px_1fr]">
      <Sidebar user={user} />
      <main className="px-[clamp(16px,4vw,56px)] pt-10 pb-[120px] min-[860px]:pb-24">
        <div className="mx-auto flex w-full max-w-[1120px] flex-col gap-7">
          <div className="flex items-center justify-between gap-3 min-[860px]:hidden">
            <Link
              href="/dashboard"
              className="focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
            >
              <Wordmark theme="light" className="h-[22px] w-auto" />
            </Link>
            <MobileLogOut />
          </div>
          {children}
        </div>
      </main>
      <MobileTabBar />
    </div>
  );
}
