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

  async function handleSubmit(values: LoginRequest) {
    setPending(true);
    setError(undefined);

    const result = await loginWithEmail(values);
    if (result.ok) {
      // stay pending through the navigation so the form cannot be resubmitted
      router.replace("/dashboard");
      router.refresh();
      return;
    }

    setError(result.error);
    setPending(false);
  }

  return (
    <LoginPanel
      titleAs="h1"
      error={error}
      pending={pending}
      onSubmit={handleSubmit}
    />
  );
}
