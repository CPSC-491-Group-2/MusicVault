"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { deleteAccount, type DeleteAccountRequest } from "@/lib/auth";
import type { AuthErrorCode, User } from "@/types/api";

import { DeleteAccountPanel } from "./DeleteAccountPanel";

export function DeleteAccountSection({ user }: { user: User }) {
  const router = useRouter();
  const [error, setError] = useState<AuthErrorCode | undefined>();
  const [fieldErrors, setFieldErrors] = useState<
    Record<string, string> | undefined
  >();
  const [pending, setPending] = useState(false);

  async function handleSubmit(values: DeleteAccountRequest) {
    setPending(true);
    setError(undefined);
    setFieldErrors(undefined);

    const result = await deleteAccount(values);

    if (result.ok) {
      router.replace("/");
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

  function handleCancel() {
    setError(undefined);
    setFieldErrors(undefined);
  }

  return (
    <DeleteAccountPanel
      user={user}
      error={error}
      fieldErrors={fieldErrors}
      pending={pending}
      onSubmit={handleSubmit}
      onCancel={handleCancel}
    />
  );
}
