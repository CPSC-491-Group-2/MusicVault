import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "quiet";
export type ButtonSize = "sm" | "md" | "lg";

type ButtonOwnProps = {
  variant: ButtonVariant;
  size: ButtonSize;
  icon?: ReactNode;
  className?: string;
  children: ReactNode;
};

type ButtonAsButtonProps = ButtonOwnProps &
  Omit<ComponentPropsWithoutRef<"button">, "className" | "children"> & {
    href?: undefined;
    external?: undefined;
  };

type ButtonAsLinkProps = ButtonOwnProps &
  Omit<ComponentPropsWithoutRef<typeof Link>, "className" | "children"> & {
    external?: false;
  };

type ButtonAsExternalLinkProps = ButtonOwnProps &
  Omit<ComponentPropsWithoutRef<"a">, "className" | "children" | "href"> & {
    href: string;
    external: true;
  };

export type ButtonProps =
  | ButtonAsButtonProps
  | ButtonAsLinkProps
  | ButtonAsExternalLinkProps;

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary: "bg-olive text-blush hover:bg-green focus-visible:bg-green",
  secondary:
    "bg-paper border-[1.5px] border-olive/25 text-olive hover:bg-blush",
  quiet: "text-olive hover:bg-blush",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "text-base px-5 py-[11px] rounded-[10px]",
  md: "text-[17px] px-6 py-[14px] rounded-[14px]",
  lg: "text-lg px-7 py-[17px] rounded-xl",
};

export function Button(props: ButtonProps) {
  const classes = [
    "inline-flex items-center justify-center gap-2 font-medium",
    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive",
    VARIANT_CLASSES[props.variant],
    SIZE_CLASSES[props.size],
    props.className,
  ]
    .filter(Boolean)
    .join(" ");

  if (props.href === undefined) {
    const {
      variant: _variant,
      size: _size,
      className: _className,
      icon,
      children,
      href: _href,
      external: _external,
      ...rest
    } = props;
    return (
      <button {...rest} type="button" className={classes}>
        {icon}
        {children}
      </button>
    );
  }

  if (props.external) {
    const {
      variant: _variant,
      size: _size,
      className: _className,
      icon,
      children,
      href,
      external: _external,
      ...rest
    } = props;
    return (
      <a {...rest} href={href} className={classes}>
        {icon}
        {children}
      </a>
    );
  }

  const {
    variant: _variant,
    size: _size,
    className: _className,
    icon,
    children,
    href,
    external: _external,
    ...rest
  } = props;
  return (
    <Link {...rest} href={href} className={classes}>
      {icon}
      {children}
    </Link>
  );
}
