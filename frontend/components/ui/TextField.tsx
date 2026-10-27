"use client";

import { useId, useState, type ComponentPropsWithoutRef } from "react";

import { Button } from "./Button";

type TextFieldProps = {
  label: string;
  type?: "text" | "email" | "password";
  hint?: string;
  error?: string;
  className?: string;
} & Omit<ComponentPropsWithoutRef<"input">, "className" | "type">;

export function TextField({
  label,
  type = "text",
  hint,
  error,
  className,
  id,
  ...rest
}: TextFieldProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;
  const hintId = `${inputId}-hint`;
  const errorId = `${inputId}-error`;
  const [passwordVisible, setPasswordVisible] = useState(false);
  const isPassword = type === "password";

  const describedBy =
    [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(" ") ||
    undefined;

  const wrapperClasses = ["flex flex-col gap-2", className]
    .filter(Boolean)
    .join(" ");

  const fieldClasses = [
    "flex h-[68px] w-full items-center gap-3 rounded-[20px] bg-paper border-[1.5px] focus-within:border-2 focus-within:border-olive",
    error ? "border-olive" : "border-olive/14",
    isPassword ? "pl-5 pr-2" : "px-5",
  ].join(" ");

  return (
    <div className={wrapperClasses}>
      <label
        htmlFor={inputId}
        className="text-[15px] font-medium leading-[1.45] text-olive"
      >
        {label}
      </label>
      {hint ? (
        <p id={hintId} className="text-[15px] leading-[1.45] text-olive/70">
          {hint}
        </p>
      ) : null}
      <div className={fieldClasses}>
        <input
          {...rest}
          id={inputId}
          type={isPassword && passwordVisible ? "text" : type}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className="h-full w-full min-w-0 bg-transparent text-[17px] text-olive outline-none placeholder:text-olive/45 disabled:cursor-not-allowed disabled:text-olive/45"
        />
        {isPassword ? (
          <Button
            variant="quiet"
            size="sm"
            aria-pressed={passwordVisible}
            disabled={rest.disabled}
            onClick={() => setPasswordVisible((visible) => !visible)}
            className="shrink-0"
          >
            {passwordVisible ? "Hide" : "Show"}
            <span className="sr-only"> password</span>
          </Button>
        ) : null}
      </div>
      {error ? (
        <p id={errorId} className="text-[15px] leading-[1.45] text-olive">
          {error}
        </p>
      ) : null}
    </div>
  );
}
