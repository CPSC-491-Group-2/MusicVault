"use client";

import { useId, useRef, useState, type FormEvent } from "react";
import { flushSync } from "react-dom";

import { authErrorMessage } from "@/components/auth/authErrors";
import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/FormMessage";
import { Surface } from "@/components/ui/Surface";
import { TextField } from "@/components/ui/TextField";
import type { DeleteAccountRequest } from "@/lib/auth";
import type { AuthErrorCode, User } from "@/types/api";

type DeleteAccountPanelProps = {
  user: User;
  error?: AuthErrorCode;
  fieldErrors?: Partial<Record<"password" | "confirm", string>>;
  pending?: boolean;
  onSubmit?: (values: DeleteAccountRequest) => void;
  onCancel?: () => void;
  className?: string;
};

const CONFIRM_PHRASE = "delete my account";
const CONFIRM_LABEL = 'Type "delete my account" to confirm';
const WARNING =
  "This permanently removes your account, your vault, your swipes and your Spotify connection from MusicVault. It can't be undone.";

export function DeleteAccountPanel({
  user,
  error,
  fieldErrors,
  pending = false,
  onSubmit,
  onCancel,
  className,
}: DeleteAccountPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [submitCount, setSubmitCount] = useState(0);
  const formRef = useRef<HTMLFormElement>(null);
  const triggerId = useId();
  const hasPassword = user.has_password;
  const confirmed = confirm.trim().toLowerCase() === CONFIRM_PHRASE;
  const passwordError =
    error === "current_password_wrong"
      ? authErrorMessage(error)
      : fieldErrors?.password;
  const panelError = error === "current_password_wrong" ? undefined : error;

  function handleExpand() {
    flushSync(() => setExpanded(true));
    formRef.current?.querySelector<HTMLElement>("input")?.focus();
  }

  function handleCancel() {
    onCancel?.();
    flushSync(() => {
      setExpanded(false);
      setConfirm("");
    });
    document.getElementById(triggerId)?.focus();
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const values: DeleteAccountRequest = { confirm };
    if (hasPassword) values.password = String(data.get("password") ?? "");
    setSubmitCount((count) => count + 1);
    onSubmit?.(values);
  }

  return (
    <Surface
      className={["flex flex-col gap-5", className].filter(Boolean).join(" ")}
    >
      <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
        Delete your account
      </h2>

      <p className="max-w-[60ch] text-[17px] leading-[1.5]">{WARNING}</p>

      {panelError ? (
        <FormMessage tone="error">{authErrorMessage(panelError)}</FormMessage>
      ) : null}

      {expanded ? (
        <form
          ref={formRef}
          noValidate
          onSubmit={handleSubmit}
          className="flex flex-col gap-5"
        >
          {hasPassword ? (
            <TextField
              label="Current password"
              type="password"
              name="password"
              autoComplete="current-password"
              required
              disabled={pending}
              error={passwordError}
              errorKey={submitCount}
            />
          ) : null}
          <TextField
            label={CONFIRM_LABEL}
            name="confirm"
            autoComplete="off"
            required
            disabled={pending}
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
            error={fieldErrors?.confirm}
            errorKey={submitCount}
          />
          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={!confirmed}
              loading={pending}
              loadingLabel="Deleting"
            >
              Delete my account
            </Button>
            <Button
              variant="quiet"
              size="md"
              disabled={pending}
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <Button
          id={triggerId}
          variant="secondary"
          size="md"
          onClick={handleExpand}
          className="self-start"
        >
          Delete account
        </Button>
      )}
    </Surface>
  );
}
