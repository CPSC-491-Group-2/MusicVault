import type { Metadata } from "next";

import { RecommendationResults } from "@/components/recommendations/RecommendationResults";
import { PageHeader } from "@/components/ui/PageHeader";

export const metadata: Metadata = {
  title: "Home · MusicVault",
};

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Welcome back"
        description="Your vault, your next finds, and what's left to set up."
      />

      <section
        aria-label="Your dashboard"
        className="grid gap-6"
      >
        <RecommendationResults />
      </section>
    </>
  );
}