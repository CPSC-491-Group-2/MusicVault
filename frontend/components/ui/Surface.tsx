import type { ReactNode } from "react";

type SurfaceTone = "paper" | "olive" | "orchid" | "dashed";
type SurfacePadding = "md" | "lg";
type SurfaceAs = "div" | "section" | "article";

type SurfaceProps = {
  tone?: SurfaceTone;
  padding?: SurfacePadding;
  as?: SurfaceAs;
  className?: string;
  children: ReactNode;
};

const TONE_CLASSES: Record<SurfaceTone, string> = {
  paper: "bg-paper text-olive",
  olive: "bg-olive text-blush",
  orchid: "bg-orchid text-olive",
  dashed: "border-2 border-dashed border-olive/22 text-olive",
};

const PADDING_CLASSES: Record<SurfacePadding, string> = {
  md: "p-7",
  lg: "p-10",
};

export function Surface({
  tone = "paper",
  padding = "md",
  as: Component = "div",
  className,
  children,
}: SurfaceProps) {
  const classes = [
    "rounded-[28px]",
    PADDING_CLASSES[padding],
    TONE_CLASSES[tone],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return <Component className={classes}>{children}</Component>;
}
