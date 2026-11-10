"use client";

import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { LoadingStack } from "./LoadingStack";

export type ButtonVariant = "primary" | "secondary" | "quiet";
export type ButtonSize = "sm" | "md" | "lg";

type ButtonOwnProps = {
  variant: ButtonVariant;
  size: ButtonSize;
  icon?: ReactNode;
  className?: string;
  children: ReactNode;
};

type ButtonLoadingProps = {
  loading?: boolean;
  progress?: number;
  loadingLabel?: string;
};

type NoLoadingProps = { [K in keyof ButtonLoadingProps]?: undefined };

type ButtonAsButtonProps = ButtonOwnProps &
  ButtonLoadingProps &
  Omit<
    ComponentPropsWithoutRef<"button">,
    "className" | "children" | "type"
  > & {
    type?: "button" | "submit";
    href?: undefined;
    external?: undefined;
  };

type ButtonAsLinkProps = ButtonOwnProps &
  NoLoadingProps &
  Omit<ComponentPropsWithoutRef<typeof Link>, "className" | "children"> & {
    external?: false;
  };

type ButtonAsExternalLinkProps = ButtonOwnProps &
  NoLoadingProps &
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

/* Pins the resting surface while loading, so hover never repaints it. */
const LOADING_HOLD_CLASSES: Record<ButtonVariant, string> = {
  primary: "hover:bg-olive!",
  secondary: "hover:bg-paper! hover:border-olive/25!",
  quiet: "hover:before:opacity-0! hover:before:scale-90!",
};

const RING_RADII: Record<ButtonSize, number> = { sm: 15, md: 19, lg: 17 };

const CELL_CLASSES =
  "col-start-1 row-start-1 inline-flex items-center justify-center gap-2 transition-[opacity,translate] duration-200 ease-mv";

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
      loading,
      progress,
      loadingLabel,
      ...rest
    } = props;

    if (loading === undefined) {
      return (
        <button {...rest} type={type} className={classes}>
          {icon}
          {children}
        </button>
      );
    }

    const percent =
      typeof progress === "number"
        ? Math.min(100, Math.max(0, progress))
        : undefined;
    const radius = RING_RADII[props.size];

    return (
      <button
        {...rest}
        type={type}
        onClick={(event) => {
          if (loading) {
            event.preventDefault();
            return;
          }
          rest.onClick?.(event);
        }}
        aria-busy={loading || undefined}
        aria-disabled={loading || undefined}
        className={`${classes} relative${loading ? ` ${LOADING_HOLD_CLASSES[props.variant]}` : ""}`}
      >
        <svg
          aria-hidden="true"
          className={`pointer-events-none absolute -inset-[6px] size-[calc(100%_+_12px)] overflow-visible transition-opacity duration-200 ease-mv ${loading ? "opacity-100" : "opacity-0"}`}
        >
          <rect
            className="stroke-olive/14"
            width="100%"
            height="100%"
            rx={radius}
            fill="none"
            strokeWidth={3}
            pathLength={100}
          />
          <rect
            className={
              percent === undefined
                ? "stroke-green animate-[mv-trace_2.2s_ease-in-out_infinite]"
                : "stroke-green transition-[stroke-dasharray] duration-[250ms] ease-mv"
            }
            width="100%"
            height="100%"
            rx={radius}
            fill="none"
            strokeWidth={3}
            pathLength={100}
            strokeDasharray="60 40"
            style={
              percent === undefined
                ? undefined
                : { strokeDasharray: `${percent} ${100 - percent}` }
            }
          />
        </svg>
        <span className="grid">
          <span
            aria-hidden={loading || undefined}
            className={`${CELL_CLASSES} ${loading ? "pointer-events-none -translate-y-[4px] opacity-0" : "translate-y-0 opacity-100"}`}
          >
            {icon}
            {children}
          </span>
          <span
            aria-hidden={loading ? undefined : true}
            className={`${CELL_CLASSES} ${loading ? "translate-y-0 opacity-100" : "pointer-events-none translate-y-[4px] opacity-0"}`}
          >
            <LoadingStack size={22} mono inline label="" />
            <span>
              {loadingLabel ?? children}
              {percent === undefined ? null : (
                <span className="tabular-nums">{` ${percent}%`}</span>
              )}
            </span>
          </span>
        </span>
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
