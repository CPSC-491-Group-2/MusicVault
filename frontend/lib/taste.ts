export type TasteNodeKind = "artist" | "tag" | "frontier";
export type TasteEdgeKind = "similar" | "tagged";

export type TasteNode = {
  id: string;
  kind: TasteNodeKind;
  label: string;
  weight: number;
};

export type TasteEdge = {
  src: string;
  dst: string;
  kind: TasteEdgeKind;
  weight: number;
};

export type TasteArtistSong = {
  id: string;
  title: string;
  album: string;
};

export type TasteArtistDetail = {
  songs: TasteArtistSong[];
};

export type TasteGraphResponse = {
  nodes: TasteNode[];
  edges: TasteEdge[];
  artists: Record<string, TasteArtistDetail>;
};

export type TasteError = "unauthorized" | "service_unavailable" | "unknown";

export type TasteGraphResult =
  | {
      ok: true;
      data: TasteGraphResponse;
    }
  | {
      ok: false;
      error: TasteError;
    };

export const TASTE_MOCKS_ENABLED =
  process.env.NEXT_PUBLIC_DISCOVERY_MOCKS === "1" ||
  !process.env.NEXT_PUBLIC_DISCOVERY_MOCKS;

const TASTE_ERROR_MESSAGES: Record<TasteError, string> = {
  unauthorized: "Sign in to see your taste graph.",
  service_unavailable: "That did not reach MusicVault. Try again in a moment.",
  unknown: "Something went wrong. Try again.",
};

export function tasteErrorMessage(error: TasteError): string {
  return TASTE_ERROR_MESSAGES[error];
}

const DEFAULT_LIMIT = 150;

function randomMockDelay(): Promise<void> {
  const ms = 300 + Math.random() * 300;
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getTasteGraph(
  options: { limit?: number } = {},
): Promise<TasteGraphResult> {
  const limit = options.limit ?? DEFAULT_LIMIT;

  if (TASTE_MOCKS_ENABLED) {
    await randomMockDelay();
    const { TASTE_GRAPH } = await import("@/data/discovery-mocks/taste-graph");

    if (limit >= TASTE_GRAPH.nodes.length) {
      return { ok: true, data: TASTE_GRAPH };
    }

    const nodes = TASTE_GRAPH.nodes.slice(0, limit);
    const keptIds = new Set(nodes.map((node) => node.id));
    const edges = TASTE_GRAPH.edges.filter(
      (edge) => keptIds.has(edge.src) && keptIds.has(edge.dst),
    );
    const artists: Record<string, TasteArtistDetail> = {};
    for (const [id, detail] of Object.entries(TASTE_GRAPH.artists)) {
      if (keptIds.has(id)) {
        artists[id] = detail;
      }
    }

    return { ok: true, data: { nodes, edges, artists } };
  }

  try {
    const response = await fetch(`/api/v1/taste/graph?limit=${limit}`, {
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
