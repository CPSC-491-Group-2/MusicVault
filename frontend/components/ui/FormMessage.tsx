import type { ReactNode } from "react";

import { CheckIcon } from "./icons";

type FormMessageTone = "error" | "success";

type FormMessageProps = {
  tone: FormMessageTone;
  className?: string;
  children: ReactNode;
};

const TONE_CLASSES: Record<FormMessageTone, string> = {
  error: "border-[1.5px] border-olive/25",
  success: "",
};

export function FormMessage({ tone, className, children }: FormMessageProps) {
  const classes = [
    "flex items-start gap-3 rounded-[18px] bg-paper px-5 py-4 text-[16px] leading-[1.5] text-olive",
    TONE_CLASSES[tone],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div role={tone === "error" ? "alert" : "status"} className={classes}>
      {tone === "success" ? (
        <CheckIcon className="h-6 w-6 shrink-0 text-green" />
      ) : null}
      <div className="min-w-0">{children}</div>
    </div>
  );
}
