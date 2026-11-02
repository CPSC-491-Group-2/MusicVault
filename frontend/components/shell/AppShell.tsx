
import Link from "next/link";
import type { ReactNode } from "react";
import type { CurrentUser } from "@/types/api";

import Wordmark from "@/components/brand/Wordmark";

import { LogoutButton } from "./LogoutButton";
import { MobileTabBar } from "./MobileTabBar";
import { Sidebar } from "./Sidebar";

type AppShellProps = {
  children: ReactNode;
  user: CurrentUser;
};

export function AppShell({ children, user }: AppShellProps) {
  return (
    <div className="min-h-dvh bg-canvas min-[860px]:grid min-[860px]:grid-cols-[260px_1fr]">
      <Sidebar user={user} />

      <main className="px-[clamp(16px,4vw,56px)] pt-10 pb-[120px] min-[860px]:pb-24">
        <div className="mx-auto flex w-full max-w-[1120px] flex-col gap-7">
          <div className="flex items-center justify-between gap-4 min-[860px]:hidden">
            <Link
              href="/dashboard"
              className="focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
            >
              <Wordmark theme="light" className="h-[22px] w-auto" />
            </Link>

            <LogoutButton />
          </div>

          {children}
        </div>
      </main>

      <MobileTabBar />
    </div>
  );
}
