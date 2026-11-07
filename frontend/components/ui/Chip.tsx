"use client";

import type { ReactNode } from "react";

import { CheckIcon } from "./icons";

export type ChipTone = "light" | "dark";

export type ChipProps = {
  pressed: boolean;
  onPressedChange?: (next: boolean) => void;
  tone?: ChipTone;
  className?: string;
  children: ReactNode;
};

const TONE_CLASSES: Record<
  ChipTone,
  { off: string; on: string; fill: string; focus: string }
> = {
  light: {
    off: "border-olive text-olive hover:bg-blush before:scale-x-0",
    on: "border-olive text-blush before:scale-x-100",
    fill: "before:absolute before:inset-0 before:-z-10 before:origin-left before:bg-olive before:transition-[transform,scale] before:duration-[250ms] before:ease-mv",
    focus:
      "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
  },
  dark: {
    off: "border-blush text-blush hover:bg-blush/15 before:scale-x-0",
    on: "border-blush text-olive before:scale-x-100",
    fill: "before:absolute before:inset-0 before:-z-10 before:origin-left before:bg-blush before:transition-[transform,scale] before:duration-[250ms] before:ease-mv",
    focus:
      "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blush",
  },
};

export function Chip({
  pressed,
  onPressedChange,
  tone = "light",
  className,
  children,
}: ChipProps) {
  const toneClasses = TONE_CLASSES[tone];

  const classes = [
    "relative isolate inline-flex items-center overflow-hidden rounded-full border px-[18px] py-2.5 text-[16px] font-medium",
    "transition-[background-color,color,transform,scale] duration-[200ms,250ms,150ms,150ms] ease-mv",
    "active:scale-[0.97]",
    toneClasses.fill,
    toneClasses.focus,
    pressed ? toneClasses.on : toneClasses.off,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  const checkClasses = [
    "inline-flex overflow-hidden transition-[width,margin,opacity] duration-200 ease-mv",
    pressed ? "w-[18px] mr-1.5 opacity-100" : "w-0 mr-0 opacity-0",
  ].join(" ");

  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={() => onPressedChange?.(!pressed)}
      className={classes}
    >
      <span className={checkClasses}>
        <CheckIcon className="h-[18px] w-[18px] shrink-0" />
      </span>
      {children}
    </button>
  );
}
