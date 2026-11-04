"use client";

import type { CSSProperties, ReactNode } from "react";
import { useCallback, useEffect, useState } from "react";

type ShellFrameProps = {
  initialCollapsed: boolean;
  sidebar: ReactNode;
  children: ReactNode;
};

type ShellStyle = CSSProperties & Record<"--sidebar-w", string>;

const SHELL = [
  "group/shell min-h-dvh bg-canvas",
  "min-[860px]:grid min-[860px]:grid-cols-[var(--sidebar-w)_1fr]",
  "transition-[grid-template-columns] duration-[250ms] ease-mv",
].join(" ");

const HANDLE = [
  "group/handle absolute top-0 right-[-22px] bottom-0 flex w-11 items-center justify-center rounded-full",
  "cursor-w-resize group-data-[collapsed]/shell:cursor-e-resize",
  "outline-offset-0 focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive",
  "transition-[outline-offset] duration-[150ms] ease-mv",
].join(" ");

const EDGE = [
  "absolute inset-y-0 left-1/2 w-[2px] -translate-x-1/2 bg-olive/25",
  "opacity-0 transition-[opacity] duration-200 ease-mv",
  "group-hover/handle:opacity-100 group-focus-visible/handle:opacity-100",
].join(" ");

const CIRCLE = [
  "relative flex size-7 scale-[0.85] items-center justify-center rounded-full",
  "border-[1.5px] border-olive/25 bg-paper text-olive opacity-0",
  "transition-[opacity,transform,scale,background-color] duration-200 ease-mv",
  "group-hover/handle:scale-100 group-hover/handle:bg-blush group-hover/handle:opacity-100",
  "group-focus-visible/handle:scale-100 group-focus-visible/handle:opacity-100",
  "group-active/handle:scale-[0.94] group-active/handle:duration-[150ms]",
].join(" ");

export function ShellFrame({
  initialCollapsed,
  sidebar,
  children,
}: ShellFrameProps) {
  const [collapsed, setCollapsed] = useState(initialCollapsed);

  const toggle = useCallback(() => {
    const next = !collapsed;

    setCollapsed(next);
    document.cookie = `mv-sidebar=${next ? "collapsed" : "open"}; path=/; max-age=31536000; SameSite=Lax`;
  }, [collapsed]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key !== "[" || event.ctrlKey || event.metaKey || event.altKey) {
        return;
      }

      const target = event.target;
      const typing =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement ||
        (target instanceof HTMLElement && target.isContentEditable);

      if (typing || !window.matchMedia("(min-width: 860px)").matches) {
        return;
      }

      toggle();
    }

    window.addEventListener("keydown", onKeyDown);

    return () => window.removeEventListener("keydown", onKeyDown);
  }, [toggle]);

  const style: ShellStyle = { "--sidebar-w": collapsed ? "76px" : "260px" };

  return (
    <div className={SHELL} data-collapsed={collapsed ? "" : undefined} style={style}>
      <div className="sticky top-0 z-20 hidden h-dvh min-[860px]:block">
        {sidebar}

        <button
          type="button"
          onClick={toggle}
          aria-expanded={!collapsed}
          aria-controls="app-sidebar"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className={HANDLE}
        >
          <span aria-hidden="true" className={EDGE} />
          <span className={CIRCLE}>
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="size-4 transition-[transform,rotate] duration-[250ms] ease-mv group-data-[collapsed]/shell:rotate-180"
            >
              <path d="M14.5 7.5 10 12l4.5 4.5" />
            </svg>
          </span>
        </button>
      </div>

      {children}
    </div>
  );
}
