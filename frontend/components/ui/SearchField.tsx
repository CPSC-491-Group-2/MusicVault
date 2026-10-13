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
    "flex h-[68px] w-full items-center gap-3 rounded-[20px] bg-paper px-5 border-[1.5px] border-olive/14 focus-within:border-2 focus-within:border-olive",
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
      <SearchIcon className="h-6 w-6 shrink-0 text-olive/45" />
      <input
        {...rest}
        type="search"
        className="h-full w-full min-w-0 bg-transparent text-[17px] text-olive outline-none placeholder:text-olive/45"
      />
    </label>
  );
}
