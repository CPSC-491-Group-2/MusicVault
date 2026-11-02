import { redirect } from "next/navigation";

import { AppShell } from "@/components/shell/AppShell";
import { getCurrentUser } from "@/lib/session";

export default async function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const user = await getCurrentUser();

  // Require an authenticated MusicVault session.
  if (!user) {
    redirect("/login");
  }

  return <AppShell user={user}>{children}</AppShell>;
}
