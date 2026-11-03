import type { ComponentPropsWithoutRef, ReactNode } from "react";

export type IconButtonSize = 48 | 56 | 76;
export type IconButtonTone = "olive" | "blush" | "paper" | "green";

type IconButtonOwnProps = {
  size: IconButtonSize;
  tone: IconButtonTone;
  label: string;
  className?: string;
  children: ReactNode;
};

export type IconButtonProps = IconButtonOwnProps &
  Omit<ComponentPropsWithoutRef<"button">, "className" | "children">;

const SIZE_CLASSES: Record<IconButtonSize, string> = {
  48: "size-12",
  56: "size-14",
  76: "size-[76px]",
};

const TONE_CLASSES: Record<IconButtonTone, string> = {
  olive: "bg-olive text-blush hover:not-disabled:bg-green",
  blush: "bg-blush text-olive hover:not-disabled:bg-orchid",
  paper: "bg-paper text-olive hover:not-disabled:bg-blush",
  green: "bg-green text-blush hover:not-disabled:bg-olive",
};

export function IconButton({
  size,
  tone,
  label,
  className,
  children,
  ...rest
}: IconButtonProps) {
  const classes = [
    "inline-flex items-center justify-center rounded-full",
    "transition-[background-color,transform,scale,outline-offset] duration-[200ms,150ms,150ms,150ms] ease-mv",
    "active:not-disabled:scale-[0.94]",
    "outline-offset-0 focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive",
    SIZE_CLASSES[size],
    TONE_CLASSES[tone],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button {...rest} type="button" aria-label={label} className={classes}>
      {children}
    </button>
  );
}
