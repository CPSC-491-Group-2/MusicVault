export interface HealthResponse {
  status: string;
  service: string;
}
// GET /api/v1/me and GET /api/v1/users/:id
export interface User {
  id: string;
  email: string | null;
  display_name: string | null;
  created_at: string;
  updated_at: string;
}
export interface Song {
  id: number;
  title: string;
  artist: string;
}
