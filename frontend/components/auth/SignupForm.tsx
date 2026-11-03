"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { registerWithEmail } from "@/lib/auth";
import type { AuthErrorCode, RegisterRequest } from "@/types/api";

import { SignupPanel } from "./SignupPanel";

export function SignupForm({ initialError }: { initialError?: string }) {
  const router = useRouter();
  const [error, setError] = useState<AuthErrorCode | undefined>(
    initialError as AuthErrorCode | undefined,
  );
  const [pending, setPending] = useState(false);

  async function handleSubmit(values: RegisterRequest) {
    setPending(true);
    setError(undefined);

    const result = await registerWithEmail(values);
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
    <SignupPanel
      titleAs="h1"
      error={error}
      pending={pending}
      onSubmit={handleSubmit}
    />
  );
}
