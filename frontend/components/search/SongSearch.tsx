"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  Button,
  FormMessage,
  SearchField,
} from "@/components/ui";

import { searchSpotifyTracks } from "@/lib/spotify";
import {
  getVault,
  saveTrackToVault,
} from "@/lib/vault";

import type { SpotifyTrack } from "@/types/api";

import { SongSearchResult } from "./SongSearchResult";

function searchErrorMessage(
  error: string,
): string {
  switch (error) {
    case "unauthorized":
      return "Sign in to search Spotify.";

    case "spotify_not_connected":
      return "Connect Spotify before searching for songs.";

    case "rate_limited":
      return "Spotify is receiving too many requests. Try again shortly.";

    case "service_unavailable":
      return "Spotify search is temporarily unavailable.";

    default:
      return "We couldn't search Spotify. Try again.";
  }
}

export function SongSearch() {
  const [query, setQuery] = useState("");
  const [tracks, setTracks] =
    useState<SpotifyTrack[]>([]);

  const [savedIds, setSavedIds] =
    useState<Set<string>>(new Set());

  const [savingIds, setSavingIds] =
    useState<Set<string>>(new Set());

  const [searching, setSearching] =
    useState(false);

  const [error, setError] =
    useState("");

  const [hasSearched, setHasSearched] =
    useState(false);

  useEffect(() => {
    async function loadVault() {
      const result = await getVault();

      if (!result.ok) {
        return;
      }

      setSavedIds(
        new Set(
          result.data.items.map(
            (song) => song.spotify_id,
          ),
        ),
      );
    }

    void loadVault();
  }, []);

  async function handleSearch(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setTracks([]);
      setHasSearched(false);
      setError("");
      return;
    }

    setSearching(true);
    setError("");

    const result =
      await searchSpotifyTracks(trimmedQuery);

    setSearching(false);
    setHasSearched(true);

    if (!result.ok) {
      setTracks([]);
      setError(
        searchErrorMessage(result.error),
      );
      return;
    }

    setTracks(result.data.items);
  }

  async function handleSave(
    track: SpotifyTrack,
  ) {
    setSavingIds((current) => {
      const next = new Set(current);
      next.add(track.spotify_id);
      return next;
    });

    const result =
      await saveTrackToVault(track);

    setSavingIds((current) => {
      const next = new Set(current);
      next.delete(track.spotify_id);
      return next;
    });

    if (!result.ok) {
      setError(
        "We couldn't save that song. Try again.",
      );
      return;
    }

    setSavedIds((current) => {
      const next = new Set(current);
      next.add(track.spotify_id);
      return next;
    });
  }

  return (
    <section
      id="song-search"
      aria-label="Song search"
      className="grid gap-7"
    >
      <form
        onSubmit={handleSearch}
        className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_auto]"
      >
        <SearchField
          label="Search for a song"
          placeholder="Search by song or artist"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
        />

        <Button
          type="submit"
          variant="primary"
          size="md"
          loading={searching}
          loadingLabel="Searching"
        >
          Search
        </Button>
      </form>

      {error ? (
        <FormMessage tone="error">
          {error}
        </FormMessage>
      ) : null}

      {hasSearched &&
      !searching &&
      tracks.length === 0 &&
      !error ? (
        <p className="text-[16px] leading-6 text-olive/70">
          No songs matched your search.
        </p>
      ) : null}

      {tracks.length > 0 ? (
        <div
          aria-label="Search results"
          className="grid gap-6 md:grid-cols-2"
        >
          {tracks.map((track) => (
            <SongSearchResult
              key={track.spotify_id}
              track={track}
              saved={savedIds.has(
                track.spotify_id,
              )}
              saving={savingIds.has(
                track.spotify_id,
              )}
              onSave={handleSave}
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}