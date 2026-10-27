import Link from "next/link";
import type { ReactNode } from "react";

import Wordmark from "@/components/brand/Wordmark";

import { MobileTabBar } from "./MobileTabBar";
import { Sidebar } from "./Sidebar";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-dvh bg-canvas min-[860px]:grid min-[860px]:grid-cols-[260px_1fr]">
      <Sidebar />
      <main className="px-[clamp(16px,4vw,56px)] pt-10 pb-[120px] min-[860px]:pb-24">
        <div className="mx-auto flex w-full max-w-[1120px] flex-col gap-7">
          <Link
            href="/dashboard"
            className="self-start focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive min-[860px]:hidden"
          >
            <Wordmark theme="light" className="h-[22px] w-auto" />
          </Link>
          {children}
        </div>
      </main>
      <MobileTabBar />
    </div>
  );
}
