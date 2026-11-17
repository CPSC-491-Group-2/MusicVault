"use client";

import { useRouter } from "next/navigation";

import { logout } from "@/lib/auth";

import { LogOutButton } from "./LogOutButton";

export function LogOutSection() {
  const router = useRouter();

  async function handleLogOut() {
    await logout();
    router.replace("/login");
    router.refresh();
  }

  return <LogOutButton onLogOut={handleLogOut} className="self-start" />;
}
