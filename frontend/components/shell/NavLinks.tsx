"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

import { NAV_ITEMS } from "./nav-items";

type NavLinksProps = {
  variant: "sidebar" | "tabbar";
};

type PillRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

const LINK_MOTION =
  "outline-offset-0 focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive transition-[color,background-color,outline-offset] duration-[200ms,200ms,150ms] ease-mv";

export function NavLinks({ variant }: NavLinksProps) {
  const pathname = usePathname();
  const isSidebar = variant === "sidebar";

  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLAnchorElement>(null);
  const [pill, setPill] = useState<PillRect | null>(null);
  const [ready, setReady] = useState(false);

  const measure = useCallback(() => {
    const container = containerRef.current;
    const active = activeRef.current;

    if (!container || !active) {
      setPill(null);
      return;
    }

    const base = container.getBoundingClientRect();
    const box = active.getBoundingClientRect();
    const next = {
      x: box.left - base.left,
      y: box.top - base.top,
      width: box.width,
      height: box.height,
    };

    setPill((prev) =>
      prev &&
      prev.x === next.x &&
      prev.y === next.y &&
      prev.width === next.width &&
      prev.height === next.height
        ? prev
        : next,
    );
  }, []);

  useLayoutEffect(() => {
    measure();
  }, [measure, pathname]);

  useLayoutEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const observer = new ResizeObserver(measure);
    observer.observe(container);

    return () => observer.disconnect();
  }, [measure]);

  // The first measured position is painted without a transition.
  useEffect(() => {
    let second = 0;
    const first = requestAnimationFrame(() => {
      second = requestAnimationFrame(() => setReady(true));
    });

    return () => {
      cancelAnimationFrame(first);
      cancelAnimationFrame(second);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative">
      <div
        aria-hidden="true"
        className={[
          "pointer-events-none absolute top-0 left-0 rounded-[14px] bg-olive",
          pill ? "opacity-100" : "opacity-0",
          ready
            ? "transition-[transform,width,height] duration-[250ms] ease-mv"
            : "transition-none",
        ].join(" ")}
        style={
          pill
            ? {
                width: pill.width,
                height: pill.height,
                transform: `translate3d(${pill.x}px, ${pill.y}px, 0)`,
              }
            : undefined
        }
      />

      <ul
        className={
          isSidebar ? "relative z-10 flex flex-col gap-1" : "relative z-10 flex"
        }
      >
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;

          const linkClasses = [
            isSidebar
              ? "flex items-center gap-3 rounded-[14px] px-[14px] py-3 text-[17px] font-medium"
              : "flex flex-col items-center gap-1 rounded-[14px] px-1 py-2 text-[12px] font-medium",
            LINK_MOTION,
            isActive ? "text-blush" : "text-olive hover:bg-blush/60",
          ];

          return (
            <li
              key={item.href}
              className={isSidebar ? undefined : "min-w-0 flex-1"}
            >
              <Link
                ref={isActive ? activeRef : null}
                href={item.href}
                data-icon={item.iconKey}
                aria-current={isActive ? "page" : undefined}
                className={linkClasses.join(" ")}
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
    </div>
  );
}
