"use client";

import type { ReactNode } from "react";

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
  { off: string; on: string; focus: string }
> = {
  light: {
    off: "border-olive text-olive",
    on: "border-olive bg-olive text-blush",
    focus:
      "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
  },
  dark: {
    off: "border-blush text-blush",
    on: "border-blush bg-blush text-olive",
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
    "rounded-full border px-[18px] py-2.5 text-[16px] font-medium",
    toneClasses.focus,
    pressed ? toneClasses.on : toneClasses.off,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={() => onPressedChange?.(!pressed)}
      className={classes}
    >
      {children}
    </button>
  );
}
