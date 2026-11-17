import type {
  RecommendationResponse,
} from "@/types/api";


export type RecommendationError =
  | "unauthorized"
  | "service_unavailable"
  | "unknown";


export type RecommendationResult =
  | {
      ok: true;
      data: RecommendationResponse;
    }
  | {
      ok: false;
      error: RecommendationError;
    };


export async function getRecommendations(): Promise<
  RecommendationResult
> {
  const response = await fetch(
    "/api/v1/recommendations",
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