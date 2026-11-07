"use client";

import { useRouter } from "next/navigation";

import { LogOutButton } from "@/components/account/LogOutButton";
import { AccountChip } from "@/components/shell/AccountChip";
import { logout } from "@/lib/auth";
import type { User } from "@/types/api";

function useLogOut() {
  const router = useRouter();

  return async function logOut() {
    await logout();
    router.replace("/login");
    router.refresh();
  };
}

type SidebarAccountProps = {
  user: User;
  className?: string;
};

export function SidebarAccount({ user, className }: SidebarAccountProps) {
  const logOut = useLogOut();

  return (
    <AccountChip
      user={user}
      onLogOut={logOut}
      className={className}
      collapsesWithSidebar
    />
  );
}

export function MobileLogOut() {
  const logOut = useLogOut();

  return <LogOutButton onLogOut={logOut} />;
}
