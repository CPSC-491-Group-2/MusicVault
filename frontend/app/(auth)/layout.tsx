import Link from "next/link";
import type { ReactNode } from "react";

import Wordmark from "@/components/brand/Wordmark";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="bg-canvas flex min-h-dvh flex-col">
      <header className="px-4 pt-7 pb-3 min-[860px]:px-16 min-[860px]:pt-7 min-[860px]:pb-7">
        <Link
          href="/"
          className="inline-block focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
        >
          <Wordmark
            theme="light"
            className="h-[22px] w-auto min-[860px]:h-[30px]"
          />
        </Link>
      </header>
      <main className="flex flex-1 flex-col items-center px-4 pt-3 pb-12 min-[860px]:justify-center min-[860px]:pt-6 min-[860px]:pb-24">
        {children}
      </main>
    </div>
  );
}
