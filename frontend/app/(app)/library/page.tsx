import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Vault · MusicVault",
};

export default function LibraryPage() {
  return (
    <>
      <PageHeader
        title="Your vault"
        description="Songs you've saved from recommendations and swipe rounds."
      />

      <section aria-label="Saved songs" className="grid gap-6">
        {/* content goes here. owned by the dashboard team, see docs/design-spec.md */}
      </section>
    </>
  );
}
