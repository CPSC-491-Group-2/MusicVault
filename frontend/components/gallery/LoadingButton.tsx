"use client";

import { useState, type ReactNode } from "react";

import { Button } from "@/components/ui/Button";

type LoadingButtonProps = {
  loadingLabel: string;
  stopLabel: string;
  progress?: number;
  children: ReactNode;
};

export function LoadingButton({
  loadingLabel,
  stopLabel,
  progress,
  children,
}: LoadingButtonProps) {
  const [loading, setLoading] = useState(false);

  return (
    <span className="inline-flex flex-wrap items-center gap-3">
      <Button
        variant="primary"
        size="md"
        loading={loading}
        progress={progress}
        loadingLabel={loadingLabel}
        onClick={() => setLoading(true)}
      >
        {children}
      </Button>
      <Button variant="secondary" size="md" onClick={() => setLoading(false)}>
        {stopLabel}
      </Button>
    </span>
  );
}
