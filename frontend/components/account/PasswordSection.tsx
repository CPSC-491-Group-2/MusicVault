"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { changePassword } from "@/lib/auth";
import type { AuthErrorCode, User } from "@/types/api";

import { PasswordPanel, type PasswordPanelValues } from "./PasswordPanel";

export function PasswordSection({ user }: { user: User }) {
  const router = useRouter();
  const [error, setError] = useState<AuthErrorCode | undefined>();
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, string> | undefined
  >();
  const [pending, setPending] = useState(false);
  const [saved, setSaved] = useState(false);
  const [formKey, setFormKey] = useState(0);

  async function handleSubmit(values: PasswordPanelValues) {
    setPending(true);
    setSaved(false);
    setError(undefined);
    setFieldErrors(undefined);

    const result = await changePassword(values);

    if (result.ok) {
      setSaved(true);
      setPending(false);
      // a new key remounts the panel, which clears the typed passwords
      setFormKey((key) => key + 1);
      router.refresh();
      return;
    }

    if (result.error === "session_revoked" || result.error === "unauthorized") {
      router.replace("/login");
      return;
    }

    setError(result.error);
    setFieldErrors(result.fieldErrors);
    setPending(false);
  }

  return (
    <PasswordPanel
      key={formKey}
      user={user}
      error={error}
      fieldErrors={fieldErrors}
      pending={pending}
      saved={saved}
      onSubmit={handleSubmit}
    />
  );
}
