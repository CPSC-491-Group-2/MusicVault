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
  Omit<
    ComponentPropsWithoutRef<"button">,
    "className" | "children" | "type"
  > & {
    type?: "button" | "submit";
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
  primary:
    "bg-olive text-blush hover:not-disabled:bg-green focus-visible:bg-green disabled:text-blush/45",
  secondary:
    "bg-paper border-[1.5px] border-olive/25 text-olive hover:not-disabled:bg-blush hover:not-disabled:border-olive/45 disabled:text-olive/45",
  quiet:
    "relative isolate text-olive disabled:text-olive/45 before:absolute before:inset-0 before:-z-10 before:rounded-[inherit] before:bg-blush before:opacity-0 before:scale-90 before:transition-[opacity,transform,scale] before:duration-200 before:ease-mv hover:not-disabled:before:opacity-100 hover:not-disabled:before:scale-100",
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "text-base px-5 py-[11px] rounded-[10px]",
  md: "text-[17px] px-6 py-[14px] rounded-[14px]",
  lg: "text-lg px-7 py-[17px] rounded-xl",
};

export function Button(props: ButtonProps) {
  const classes = [
    "inline-flex items-center justify-center gap-2 font-medium disabled:cursor-not-allowed",
    "transition-[background-color,border-color,color,transform,scale,outline-offset] duration-[200ms,200ms,200ms,150ms,150ms,150ms] ease-mv",
    "active:not-disabled:scale-[0.98]",
    "outline-offset-0 focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive",
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
      type = "button",
      ...rest
    } = props;
    return (
      <button {...rest} type={type} className={classes}>
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
