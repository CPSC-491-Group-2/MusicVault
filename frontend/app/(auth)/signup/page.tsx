import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { SignupForm } from "@/components/auth/SignupForm";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Sign up · MusicVault",
};

export default async function SignupPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string | string[] }>;
}) {
  const user = await getCurrentUser();
  if (user) redirect("/dashboard");

  const raw = (await searchParams).error;
  const initialError = Array.isArray(raw) ? raw[0] : raw;

  return <SignupForm initialError={initialError} />;
}
