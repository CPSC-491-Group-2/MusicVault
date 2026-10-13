import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Profile · MusicVault",
};

export default function ProfilePage() {
  return (
    <>
      <PageHeader
        title="Profile"
        description="Your account and your Spotify connection."
      />

      <section aria-label="Account and connection" className="grid gap-6">
        {/* content goes here. owned by the dashboard team, see docs/design-spec.md */}
      </section>
    </>
  );
}
