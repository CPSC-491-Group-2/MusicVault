import type { Metadata } from "next";

import { SwipeDeck } from "@/components/swipe/SwipeDeck";
import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Swipe · MusicVault",
};

export default async function SwipePage({
  searchParams,
}: {
  searchParams: Promise<{ seed?: string; mockFail?: string }>;
}) {
  const { seed, mockFail } = await searchParams;

  return (
    <>
      <PageHeader
        title="Swipe to tune"
        description="Keep or pass on a round of songs. Every swipe sharpens what we recommend next."
      />

      <section aria-label="Swipe deck" className="grid gap-6">
        <SwipeDeck seed={seed ?? null} simulateFailure={mockFail === "1"} />
      </section>
    </>
  );
}
