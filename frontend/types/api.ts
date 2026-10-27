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
  | "email_taken";
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
