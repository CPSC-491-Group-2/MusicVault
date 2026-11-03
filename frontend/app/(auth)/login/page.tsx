import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { LoginForm } from "@/components/auth/LoginForm";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Log in · MusicVault",
};

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string | string[] }>;
}) {
  const user = await getCurrentUser();
  if (user) redirect("/dashboard");

  const raw = (await searchParams).error;
  const initialError = Array.isArray(raw) ? raw[0] : raw;

  return <LoginForm initialError={initialError} />;
}
