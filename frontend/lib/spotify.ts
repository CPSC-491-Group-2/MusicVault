import type { SpotifyTrack } from "@/types/api";

export interface SpotifySearchResponse {
  items: SpotifyTrack[];
  total: number;
  limit: number;
  offset: number;
  next: string | null;
  previous: string | null;
}

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