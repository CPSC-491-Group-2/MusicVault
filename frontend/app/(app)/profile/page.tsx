import type { Metadata } from "next";

import { AccountDetailsPanel } from "@/components/account/AccountDetailsPanel";
import { LogOutSection } from "@/components/account/LogOutSection";
import { PasswordSection } from "@/components/account/PasswordSection";
import { SpotifySection } from "@/components/account/SpotifySection";
import { PageHeader } from "@/components/ui/PageHeader";
import { requireUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Profile · MusicVault",
};

export default async function ProfilePage({
  searchParams,
}: {
  searchParams: Promise<{
    spotify?: string | string[];
    error?: string | string[];
  }>;
}) {
  const user = await requireUser();

  const { spotify: rawSpotify, error: rawError } = await searchParams;
  const spotify = Array.isArray(rawSpotify) ? rawSpotify[0] : rawSpotify;
  const error = Array.isArray(rawError) ? rawError[0] : rawError;

  return (
    <>
      <PageHeader
        title="Profile"
        description="Your account and your Spotify connection."
      />

      <section aria-label="Account and connection" className="grid gap-6">
        <AccountDetailsPanel user={user} />
        <PasswordSection user={user} />
        <SpotifySection user={user} spotify={spotify} error={error} />
      </section>

      <LogOutSection />
    </>
  );
}
