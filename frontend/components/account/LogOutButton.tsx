"use client";

import { Button } from "@/components/ui/Button";

type LogOutButtonProps = {
  onLogOut?: () => void;
  className?: string;
};

export function LogOutButton({ onLogOut, className }: LogOutButtonProps) {
  return (
    <Button variant="quiet" size="sm" onClick={onLogOut} className={className}>
      Log out
    </Button>
  );
}
