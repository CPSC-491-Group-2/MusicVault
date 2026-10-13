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
  olive: "bg-olive text-blush",
  blush: "bg-blush text-olive",
  paper: "bg-paper text-olive",
  green: "bg-green text-blush",
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
    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
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
