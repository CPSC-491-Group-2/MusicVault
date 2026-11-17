export type SwipeSong = {
  id: string;
  title: string;
  artist: string;
  album: string;
  album_image_url: string | null;
  preview_url: string | null;
  spotify_url: string | null;
};

export type SwipeReason = {
  text: string;
  path: string[];
};

export type SwipeScoreComponents = {
  graph: number;
  similarity: number;
  discovery: number;
};

export type DeckItem = {
  song: SwipeSong;
  reason: SwipeReason;
  score: number;
  components: SwipeScoreComponents;
};

export type DeckResponse = {
  items: DeckItem[];
  algorithm_version: string;
};

export type SwipeAction = "keep" | "pass" | "skip";

export type SwipeRecord = {
  song_id: string;
  preference_type: string;
};

export type DiscoveryError = "unauthorized" | "service_unavailable" | "unknown";

export type DeckResult =
  | {
      ok: true;
      data: DeckResponse;
    }
  | {
      ok: false;
      error: DiscoveryError;
    };

export type SwipeResult =
  | {
      ok: true;
      data: SwipeRecord;
    }
  | {
      ok: false;
      error: DiscoveryError;
    };

export const DISCOVERY_MOCKS_ENABLED =
  process.env.NEXT_PUBLIC_DISCOVERY_MOCKS === "1" ||
  !process.env.NEXT_PUBLIC_DISCOVERY_MOCKS;

const DISCOVERY_ERROR_MESSAGES: Record<DiscoveryError, string> = {
  unauthorized: "Sign in to keep tuning your recommendations.",
  service_unavailable: "That did not reach MusicVault. Try again in a moment.",
  unknown: "Something went wrong. Try again.",
};

export function discoveryErrorMessage(error: DiscoveryError): string {
  return DISCOVERY_ERROR_MESSAGES[error];
}

const ALGORITHM_VERSION = "mock-v1";
const SEED_ARTIST_PREFIX = "artist:";

function randomMockDelay(): Promise<void> {
  const ms = 300 + Math.random() * 300;
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getDeck(
  options: {
    limit?: number;
    exclude?: readonly string[];
    seed?: string | null;
  } = {},
): Promise<DeckResult> {
  const limit = options.limit ?? 10;
  const exclude = new Set(options.exclude ?? []);

  if (DISCOVERY_MOCKS_ENABLED) {
    await randomMockDelay();
    const { DECK_POOL, songsForArtist } = await import(
      "@/data/discovery-mocks/song-pool"
    );

    const seedSlug = options.seed?.startsWith(SEED_ARTIST_PREFIX)
      ? options.seed.slice(SEED_ARTIST_PREFIX.length)
      : null;
    const seeded = seedSlug ? songsForArtist(seedSlug) : [];
    const ordered = seeded.length > 0
      ? [...seeded, ...DECK_POOL.filter((item) => !seeded.includes(item))]
      : DECK_POOL;

    const items = ordered
      .filter((item) => !exclude.has(item.song.id))
      .slice(0, limit);

    return {
      ok: true,
      data: { items, algorithm_version: ALGORITHM_VERSION },
    };
  }

  try {
    const params = new URLSearchParams();
    params.set("limit", String(limit));
    if (exclude.size > 0) {
      params.set("exclude", [...exclude].join(","));
    }
    if (options.seed) {
      params.set("seed", options.seed);
    }

    const response = await fetch(`/api/v1/swipe/deck?${params.toString()}`, {
      method: "GET",
      credentials: "same-origin",
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }
    if (response.status === 401) {
      return { ok: false, error: "unauthorized" };
    }
    if (response.status >= 500) {
      return { ok: false, error: "service_unavailable" };
    }
    return { ok: false, error: "unknown" };
  } catch {
    return { ok: false, error: "service_unavailable" };
  }
}

const PREFERENCE_TYPE_BY_ACTION: Record<SwipeAction, string> = {
  keep: "liked",
  pass: "disliked",
  skip: "skipped",
};

export async function postSwipe(
  input: { song_id: string; action: SwipeAction; deck_position: number },
  options: { simulateFailure?: boolean } = {},
): Promise<SwipeResult> {
  if (DISCOVERY_MOCKS_ENABLED) {
    await randomMockDelay();
    if (options.simulateFailure) {
      return { ok: false, error: "service_unavailable" };
    }
    return {
      ok: true,
      data: {
        song_id: input.song_id,
        preference_type: PREFERENCE_TYPE_BY_ACTION[input.action],
      },
    };
  }

  try {
    const response = await fetch("/api/v1/swipe", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });

    if (response.ok) {
      return { ok: true, data: await response.json() };
    }
    if (response.status === 401) {
      return { ok: false, error: "unauthorized" };
    }
    if (response.status >= 500) {
      return { ok: false, error: "service_unavailable" };
    }
    return { ok: false, error: "unknown" };
  } catch {
    return { ok: false, error: "service_unavailable" };
  }
}
