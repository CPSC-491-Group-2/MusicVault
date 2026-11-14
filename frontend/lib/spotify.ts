//import type { SpotifyTrack } from "@/types/api";

import type {
  SpotifySearchResponse,
} from "@/types/api";



export type SpotifySearchErrorCode =
  | "unauthorized"
  | "spotify_not_connected"
  | "rate_limited"
  | "service_unavailable"
  | "unknown";

export type SpotifySearchResult =
  | {
      ok: true;
      data: SpotifySearchResponse;
    }
  | {
      ok: false;
      error: SpotifySearchErrorCode;
    };

export async function searchSpotifyTracks(
  query: string,
): Promise<SpotifySearchResult> {
  const trimmedQuery = query.trim();

  if (!trimmedQuery) {
    return {
      ok: true,
      data: {
        items: [],
        total: 0,
        limit: 12,
        offset: 0,
        next: null,
        previous: null,
      },
    };
  }

  const params = new URLSearchParams({
    q: trimmedQuery,
    limit: "12",
  });

  const response = await fetch(
    `/api/v1/spotify/search?${params.toString()}`,
    {
      method: "GET",
      credentials: "same-origin",
    },
  );

  if (response.ok) {
    return {
      ok: true,
      data: await response.json(),
    };
  }

  if (response.status === 401) {
    return {
      ok: false,
      error: "unauthorized",
    };
  }

  if (response.status === 403) {
    return {
      ok: false,
      error: "spotify_not_connected",
    };
  }

  if (response.status === 429) {
    return {
      ok: false,
      error: "rate_limited",
    };
  }

  if (response.status >= 500) {
    return {
      ok: false,
      error: "service_unavailable",
    };
  }

  return {
    ok: false,
    error: "unknown",
  };
}