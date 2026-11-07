import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Taste · MusicVault",
};

export default function TastePage() {
  return (
    <>
      <PageHeader
        title="Your taste"
        description="What we've picked up from your listening and your swipes."
      />

      <section aria-label="Taste insights" className="grid gap-6">
        {/* content goes here. owned by the dashboard team, see docs/design-spec.md */}
      </section>
    </>
  );
}
