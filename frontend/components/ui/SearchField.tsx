import type { ComponentPropsWithoutRef } from "react";

import { SearchIcon } from "./icons";

type SearchFieldProps = {
  label: string;
  labelVisible?: boolean;
  className?: string;
} & Omit<ComponentPropsWithoutRef<"input">, "className" | "type">;

export function SearchField({
  label,
  labelVisible = false,
  className,
  ...rest
}: SearchFieldProps) {
  const wrapperClasses = [
    "group flex h-[68px] w-full items-center gap-3 rounded-[20px] bg-paper px-5 border-[1.5px] border-olive/14 hover:border-olive/25 focus-within:border-olive outline-offset-0 focus-within:outline-2 focus-within:outline-solid focus-within:outline-offset-2 focus-within:outline-olive transition-[border-color,outline-offset] duration-[200ms,150ms] ease-mv",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <label className={wrapperClasses}>
      <span
        className={
          labelVisible
            ? "shrink-0 text-[15px] font-medium text-olive"
            : "sr-only"
        }
      >
        {label}
      </span>
      <SearchIcon className="h-6 w-6 shrink-0 text-olive/45 transition-[color] duration-200 ease-mv group-focus-within:text-olive" />
      <input
        {...rest}
        type="search"
        className="h-full w-full min-w-0 bg-transparent text-[17px] text-olive outline-none placeholder:text-olive/45"
      />
    </label>
  );
}
