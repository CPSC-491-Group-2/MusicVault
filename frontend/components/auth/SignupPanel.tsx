"use client";

import { useState, type FormEvent } from "react";
import { flushSync } from "react-dom";

import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/FormMessage";
import { Surface } from "@/components/ui/Surface";
import { TextField } from "@/components/ui/TextField";
import type { AuthErrorCode, RegisterRequest } from "@/types/api";

import { authErrorMessage } from "./authErrors";
import { SpotifyContinueButton } from "./SpotifyContinueButton";

type SignupPanelProps = {
  titleAs?: "h1" | "h2";
  error?: AuthErrorCode;
  pending?: boolean;
  onSubmit?: (values: RegisterRequest) => void;
  className?: string;
};

type FieldErrors = {
  email?: string;
  password?: string;
};

const TITLE_CLASSES: Record<"h1" | "h2", string> = {
  h1: "text-balance text-[32px] font-semibold leading-[1.05] tracking-[-0.03em] min-[860px]:text-[44px]",
  h2: "text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]",
};

export function SignupPanel({
  titleAs: Title = "h1",
  error,
  pending = false,
  onSubmit,
  className,
}: SignupPanelProps) {
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const displayName = String(data.get("display_name") ?? "").trim();
    const email = String(data.get("email") ?? "")
      .trim()
      .toLowerCase();
    const password = String(data.get("password") ?? "");
    const emailInput = form.elements.namedItem("email");

    const nextErrors: FieldErrors = {};
    if (!email) {
      nextErrors.email = "Enter your email";
    } else if (
      emailInput instanceof HTMLInputElement &&
      emailInput.validity.typeMismatch
    ) {
      nextErrors.email = "Enter an email like name@example.com";
    }
    if (password.length < 8) {
      nextErrors.password = "Use at least 8 characters";
    } else if (password.length > 128) {
      nextErrors.password = "Use 128 characters or fewer";
    }

    flushSync(() => setFieldErrors(nextErrors));

    if (nextErrors.email || nextErrors.password) {
      form.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus();
      return;
    }

    const values: RegisterRequest = { email, password };
    if (displayName) values.display_name = displayName;
    onSubmit?.(values);
  }

  return (
    <Surface
      padding="lg"
      className={["flex w-full max-w-[480px] flex-col gap-6", className]
        .filter(Boolean)
        .join(" ")}
    >
      <Title className={TITLE_CLASSES[Title]}>Create your account</Title>

      {error ? (
        <FormMessage tone="error">{authErrorMessage(error)}</FormMessage>
      ) : null}

      <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-5">
        <TextField
          label="Name"
          name="display_name"
          autoComplete="name"
          hint="Shown on your profile"
          disabled={pending}
        />
        <TextField
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          required
          disabled={pending}
          error={fieldErrors.email}
        />
        <TextField
          label="Password"
          type="password"
          name="password"
          autoComplete="new-password"
          hint="8 to 128 characters"
          required
          disabled={pending}
          error={fieldErrors.password}
        />
        <Button
          type="submit"
          variant="primary"
          size="lg"
          disabled={pending}
          aria-busy={pending || undefined}
          className="w-full"
        >
          {pending ? "Creating account" : "Create account"}
        </Button>
      </form>

      <p className="text-center text-[15px] leading-[1.45] text-olive/70">or</p>

      <SpotifyContinueButton size="lg" className="w-full" />

      <p className="flex flex-wrap items-center gap-x-1 text-[15px] leading-[1.45] text-olive/70">
        Already have an account?
        <Button variant="quiet" size="sm" href="/login">
          Log in
        </Button>
      </p>
    </Surface>
  );
}
