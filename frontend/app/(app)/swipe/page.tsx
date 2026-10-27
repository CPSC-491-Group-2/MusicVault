import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Swipe · MusicVault",
};

export default function SwipePage() {
  return (
    <>
      <PageHeader
        title="Swipe to tune"
        description="Keep or pass on a round of songs. Every swipe sharpens what we recommend next."
      />

      <section aria-label="Swipe deck" className="grid gap-6">
        {/* content goes here. owned by the dashboard team, see docs/design-spec.md */}
      </section>
    </>
  );
}
