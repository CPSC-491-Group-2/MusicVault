export interface HealthResponse {
  status: string;
  service: string;
}
// GET /api/v1/me and GET /api/v1/users/:id
export interface User {
  id: string;
  email: string | null;
  display_name: string | null;
  has_password: boolean;
  spotify: {
    connected: boolean;
    display_name: string | null;
  };
  created_at: string;
  updated_at: string;
}
export type AuthErrorCode =
  | "invalid_state"
  | "access_denied"
  | "spotify_error"
  | "spotify_not_allowed"
  | "spotify_in_use"
  | "already_connected"
  | "invalid_credentials"
  | "email_taken"
  | "service_unavailable";
export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}
export interface LoginRequest {
  email: string;
  password: string;
}
export interface Song {
  id: number;
  title: string;
  artist: string;
}

//adding type for spotify track 
export interface SpotifyArtist {
  spotify_id: string;
  name: string;
}

export interface SpotifyAlbum {
  spotify_id: string | null;
  name: string | null;
  image_url: string | null;
}

export interface SpotifyTrack {
  spotify_id: string;
  title: string;
  artists: SpotifyArtist[];
  album: SpotifyAlbum;
  duration_ms: number | null;
  popularity: number | null;
  explicit: boolean;
  spotify_url: string | null;
}