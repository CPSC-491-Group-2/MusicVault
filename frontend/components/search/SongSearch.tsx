"use client";

import { useState } from "react";

import { SearchField } from "@/components/ui";

export function SongSearch() {
  const [query, setQuery] = useState("");

  return (
    <section
      id="song-search"
      aria-label="Song search"
      className="grid gap-6"
    >
      <SearchField
        label="Search for a song"
        placeholder="Search by song or artist"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />

      <p className="text-[16px] leading-6 text-olive/70">
        Search Spotify for a song you already love.
      </p>
    </section>
  );
}