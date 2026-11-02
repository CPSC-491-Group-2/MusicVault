import type { HealthResponse } from "../types/api";

// Browser requests use the Next.js same-origin API proxy.
export const API_URL = "/api";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/v1/health`);

  if (!response.ok) {
    throw new Error("Failed to connect to API");
  }

  return response.json();
}