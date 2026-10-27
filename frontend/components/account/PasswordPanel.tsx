"use client";

import { useState, type FormEvent } from "react";
import { flushSync } from "react-dom";

import { authErrorMessage } from "@/components/auth/authErrors";
import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/FormMessage";
import { Surface } from "@/components/ui/Surface";
import { TextField } from "@/components/ui/TextField";
import type { AuthErrorCode, User } from "@/types/api";

export type PasswordPanelValues = {
  current_password?: string;
  email?: string;
  new_password: string;
};

type PasswordPanelProps = {
  user: User;
  error?: AuthErrorCode;
  pending?: boolean;
  saved?: boolean;
  onSubmit?: (values: PasswordPanelValues) => void;
  className?: string;
};

type FieldErrors = {
  current_password?: string;
  email?: string;
  new_password?: string;
};

export function PasswordPanel({
  user,
  error,
  pending = false,
  saved = false,
  onSubmit,
  className,
}: PasswordPanelProps) {
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const hasPassword = user.has_password;
  const needsEmail = !hasPassword && user.email === null;
  const submitLabel = hasPassword ? "Change password" : "Add password";
  const intro =
    user.email === null
      ? "Add an email and password so you can log in without Spotify."
      : "Add a password so you can log in without Spotify.";

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const currentPassword = String(data.get("current_password") ?? "");
    const email = String(data.get("email") ?? "")
      .trim()
      .toLowerCase();
    const newPassword = String(data.get("new_password") ?? "");
    const emailInput = form.elements.namedItem("email");

    const nextErrors: FieldErrors = {};
    if (hasPassword && !currentPassword) {
      nextErrors.current_password = "Enter your current password";
    }
    if (needsEmail) {
      if (!email) {
        nextErrors.email = "Enter your email";
      } else if (
        emailInput instanceof HTMLInputElement &&
        emailInput.validity.typeMismatch
      ) {
        nextErrors.email = "Enter an email like name@example.com";
      }
    }
    if (newPassword.length < 8) {
      nextErrors.new_password = "Use at least 8 characters";
    } else if (newPassword.length > 128) {
      nextErrors.new_password = "Use 128 characters or fewer";
    }

    flushSync(() => setFieldErrors(nextErrors));

    if (
      nextErrors.current_password ||
      nextErrors.email ||
      nextErrors.new_password
    ) {
      form.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus();
      return;
    }

    const values: PasswordPanelValues = { new_password: newPassword };
    if (hasPassword) values.current_password = currentPassword;
    if (needsEmail) values.email = email;
    onSubmit?.(values);
  }

  return (
    <Surface
      className={["flex flex-col gap-5", className].filter(Boolean).join(" ")}
    >
      <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
        {hasPassword ? "Password" : "Add a password"}
      </h2>

      {hasPassword ? null : (
        <p className="max-w-[60ch] text-[17px] leading-[1.5] text-olive/70">
          {intro}
        </p>
      )}

      {saved ? <FormMessage tone="success">Password saved</FormMessage> : null}
      {error ? (
        <FormMessage tone="error">{authErrorMessage(error)}</FormMessage>
      ) : null}

      <form noValidate onSubmit={handleSubmit} className="flex flex-col gap-5">
        {hasPassword ? (
          <TextField
            label="Current password"
            type="password"
            name="current_password"
            autoComplete="current-password"
            required
            disabled={pending}
            error={fieldErrors.current_password}
          />
        ) : null}
        {needsEmail ? (
          <TextField
            label="Email"
            type="email"
            name="email"
            autoComplete="email"
            required
            disabled={pending}
            error={fieldErrors.email}
          />
        ) : null}
        <TextField
          label="New password"
          type="password"
          name="new_password"
          autoComplete="new-password"
          hint="8 to 128 characters"
          required
          disabled={pending}
          error={fieldErrors.new_password}
        />
        <Button
          type="submit"
          variant="primary"
          size="md"
          disabled={pending}
          aria-busy={pending || undefined}
          className="self-start"
        >
          {pending ? "Saving" : submitLabel}
        </Button>
      </form>
    </Surface>
  );
}
