import type { ReactNode } from "react";

export type TagTone = "light" | "dark";

export type TagProps = {
  tone?: TagTone;
  className?: string;
  children: ReactNode;
};

const TONE_CLASSES: Record<TagTone, string> = {
  light: "bg-canvas text-olive",
  dark: "bg-blush/15 text-blush",
};

export function Tag({ tone = "light", className, children }: TagProps) {
  const classes = [
    "inline-flex items-center rounded-full px-3 py-1.5 text-[14px] font-medium",
    TONE_CLASSES[tone],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <span className={classes}>{children}</span>;
}
