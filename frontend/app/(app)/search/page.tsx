import type { Metadata } from "next";

import { PageHeader } from "@/components/ui/PageHeader";
import { SongSearch } from "@/components/search/SongSearch";

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

      <SongSearch />     
    </>
  );
}
