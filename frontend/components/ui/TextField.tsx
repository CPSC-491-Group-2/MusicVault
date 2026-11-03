"use client";

import {
  useEffect,
  useId,
  useRef,
  useState,
  type ComponentPropsWithoutRef,
} from "react";

import { Button } from "./Button";
import { WarningIcon } from "./icons";

type TextFieldProps = {
  label: string;
  type?: "text" | "email" | "password";
  hint?: string;
  error?: string;
  errorKey?: number | string;
  className?: string;
} & Omit<ComponentPropsWithoutRef<"input">, "className" | "type">;

export function TextField({
  label,
  type = "text",
  hint,
  error,
  errorKey,
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
  const fieldRef = useRef<HTMLDivElement>(null);
  const errorSignature = `${errorKey ?? ""}|${error ?? ""}`;
  const lastErrorSignature = useRef<string | null>(null);

  useEffect(() => {
    const previous = lastErrorSignature.current;
    lastErrorSignature.current = errorSignature;
    const field = fieldRef.current;
    if (previous === null || previous === errorSignature || !error || !field) {
      return;
    }
    // the forced reflow is what lets a repeated message shake again
    field.classList.remove("mv-shake");
    void field.offsetWidth;
    field.classList.add("mv-shake");
  }, [error, errorSignature]);

  const describedBy =
    [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(" ") ||
    undefined;

  const wrapperClasses = ["flex flex-col gap-2", className]
    .filter(Boolean)
    .join(" ");

  const fieldClasses = [
    "flex h-[68px] w-full items-center gap-3 rounded-[20px] bg-paper border-[1.5px] outline-offset-0 focus-within:outline-2 focus-within:outline-solid focus-within:outline-offset-2 transition-[border-color,outline-offset] duration-[200ms,150ms] ease-mv",
    error
      ? "border-red focus-within:border-red focus-within:outline-red"
      : "border-olive/14 hover:border-olive/25 focus-within:border-olive focus-within:outline-olive",
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
      <div
        ref={fieldRef}
        className={fieldClasses}
        onAnimationEnd={(event) => {
          if (event.target === event.currentTarget) {
            fieldRef.current?.classList.remove("mv-shake");
          }
        }}
      >
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
      <div
        aria-live="polite"
        className={[
          // the negative margin cancels the column gap while the message is collapsed
          "-mt-2 grid transition-[grid-template-rows,opacity] duration-200 ease-mv",
          error ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
        ].join(" ")}
      >
        <div className="overflow-hidden">
          {error ? (
            <p
              id={errorId}
              className="flex items-start gap-2 pt-2 text-[15px] font-medium leading-[1.45] text-red"
            >
              <WarningIcon className="mt-[2px] h-[18px] w-[18px] shrink-0" />
              {error}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
