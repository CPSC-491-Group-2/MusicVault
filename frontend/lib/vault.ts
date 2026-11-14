import type { SpotifyTrack } from "@/types/api";

export type VaultError =
  | "unauthorized"
  | "not_found"
  | "service_unavailable"
  | "unknown";

export type VaultResult<T> =
  | {
      ok: true;
      data: T;
    }
  | {
      ok: false;
      error: VaultError;
    };

export interface SavedSong {
  spotify_id: string;
}

export interface VaultResponse {
  items: SavedSong[];
}

export async function getVault(): Promise<
  VaultResult<VaultResponse>
> {
  const response = await fetch("/api/v1/vault", {
    method: "GET",
    credentials: "same-origin",
  });

  if (response.ok) {
    return {
      ok: true,
      data: await response.json(),
    };
  }

  if (response.status === 401) {
    return { ok: false, error: "unauthorized" };
  }

  if (response.status >= 500) {
    return { ok: false, error: "service_unavailable" };
  }

  return { ok: false, error: "unknown" };
}

export async function saveTrackToVault(
  track: SpotifyTrack,
): Promise<VaultResult<SavedSong>> {
  const response = await fetch("/api/v1/vault", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      track,
    }),
  });

  if (response.ok) {
    return {
      ok: true,
      data: await response.json(),
    };
  }

  if (response.status === 401) {
    return { ok: false, error: "unauthorized" };
  }

  if (response.status === 404) {
    return { ok: false, error: "not_found" };
  }

  if (response.status >= 500) {
    return { ok: false, error: "service_unavailable" };
  }

  return { ok: false, error: "unknown" };
}