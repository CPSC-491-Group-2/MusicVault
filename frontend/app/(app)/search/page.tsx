import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Search · MusicVault",
};

export default function SearchPage() {
  return (
    <>
      <PageHeader
        title="Find a song you love"
        description="Pick a few starting songs. We dig from there."
      />

      <section aria-label="Song search" className="grid gap-6">
        {/* content goes here. owned by the dashboard team, see docs/design-spec.md */}
      </section>
    </>
  );
}
