import { HealthResponse, SpotifyTrack,  } from "../types/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:5000";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/v1/health`);

  if (!response.ok) {
    throw new Error("Failed to connect to API");
  }

  return response.json();
}

export async function getSpotifyTopTracks(): Promise<SpotifyTrack[]> {
  const response = await fetch(
    `${API_URL}/api/v1/spotify/top-tracks?limit=20&time_range=medium_term&offset=0`,
    {
      credentials: "include",
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("You must log in first.");
    }

    if (response.status === 403) {
      throw new Error("Spotify account is not connected.");
    }

    throw new Error("Failed to retrieve Spotify top tracks.");
  }

  return response.json();
}