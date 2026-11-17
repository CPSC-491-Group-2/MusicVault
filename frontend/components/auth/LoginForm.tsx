"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { loginWithEmail } from "@/lib/auth";
import type { AuthErrorCode, LoginRequest } from "@/types/api";

import { LoginPanel } from "./LoginPanel";

export function LoginForm({ initialError }: { initialError?: string }) {
  const router = useRouter();
  const [error, setError] = useState<AuthErrorCode | undefined>(
    initialError as AuthErrorCode | undefined,
  );
  const [pending, setPending] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, string> | undefined
  >();

  async function handleSubmit(values: LoginRequest) {
    setPending(true);
    setError(undefined);
    setFieldErrors(undefined);

    const result = await loginWithEmail(values);
    if (result.ok) {
      // stay pending through the navigation so the form cannot be resubmitted
      router.replace("/dashboard");
      router.refresh();
      return;
    }

    setError(result.error);
    setFieldErrors(result.fieldErrors);
    setPending(false);
  }

  return (
    <LoginPanel
      titleAs="h1"
      error={error}
      fieldErrors={fieldErrors}
      pending={pending}
      onSubmit={handleSubmit}
    />
  );
}
