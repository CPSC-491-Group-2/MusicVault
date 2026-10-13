"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV_ITEMS } from "./nav-items";

type NavLinksProps = {
  variant: "sidebar" | "tabbar";
};

export function NavLinks({ variant }: NavLinksProps) {
  const pathname = usePathname();
  const isSidebar = variant === "sidebar";

  return (
    <ul className={isSidebar ? "flex flex-col gap-1" : "flex"}>
      {NAV_ITEMS.map((item) => {
        const isActive =
          pathname === item.href || pathname.startsWith(item.href + "/");
        const Icon = item.icon;

        const linkClasses = isSidebar
          ? [
              "flex items-center gap-3 rounded-[14px] px-[14px] py-3 text-[17px] font-medium",
              "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
              isActive ? "bg-olive text-blush" : "hover:bg-blush/60",
            ]
          : [
              "flex flex-col items-center gap-1 rounded-[14px] px-1 py-2 text-[12px] font-medium",
              "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
              isActive ? "bg-olive text-blush" : "text-olive",
            ];

        return (
          <li
            key={item.href}
            className={isSidebar ? undefined : "min-w-0 flex-1"}
          >
            <Link
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={linkClasses.filter(Boolean).join(" ")}
            >
              <Icon className="h-[22px] w-[22px] shrink-0" />
              {isSidebar ? (
                item.label
              ) : (
                <span className="truncate">{item.label}</span>
              )}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
