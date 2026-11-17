import type { TasteEdge, TasteGraphResponse, TasteNode } from "@/lib/taste";

export type TasteGraphIndex = {
  nodeById: Map<string, TasteNode>;
  neighbors: Map<string, Set<string>>;
};

export type TasteListGroup = {
  key: string;
  label: string;
  kind: "tag" | "artist" | "frontier";
  artists: TasteNode[];
};

function byLabel(a: TasteNode, b: TasteNode): number {
  return a.label.localeCompare(b.label);
}

/* Built from the response edges, before the graph library rewrites them. */
export function buildIndex(
  nodes: TasteNode[],
  edges: TasteEdge[],
): TasteGraphIndex {
  const nodeById = new Map<string, TasteNode>();
  const neighbors = new Map<string, Set<string>>();

  for (const node of nodes) {
    nodeById.set(node.id, node);
    neighbors.set(node.id, new Set<string>());
  }

  for (const edge of edges) {
    neighbors.get(edge.src)?.add(edge.dst);
    neighbors.get(edge.dst)?.add(edge.src);
  }

  return { nodeById, neighbors };
}

export function neighborArtists(
  index: TasteGraphIndex,
  id: string,
): TasteNode[] {
  const ids = index.neighbors.get(id);
  if (!ids) {
    return [];
  }

  return [...ids]
    .map((neighborId) => index.nodeById.get(neighborId))
    .filter(
      (node): node is TasteNode =>
        node !== undefined && node.kind !== "tag",
    )
    .sort(byLabel);
}

export function buildGroups(
  data: TasteGraphResponse,
  index: TasteGraphIndex,
): TasteListGroup[] {
  const groups: TasteListGroup[] = [];
  const grouped = new Set<string>();

  const tags = data.nodes
    .filter((node) => node.kind === "tag")
    .sort((a, b) => b.weight - a.weight || byLabel(a, b));

  for (const tag of tags) {
    const artists = neighborArtists(index, tag.id).filter(
      (node) => node.kind === "artist",
    );

    if (artists.length === 0) {
      continue;
    }

    for (const artist of artists) {
      grouped.add(artist.id);
    }

    groups.push({
      key: tag.id,
      label: tag.label,
      kind: "tag",
      artists,
    });
  }

  const ungrouped = data.nodes
    .filter((node) => node.kind === "artist" && !grouped.has(node.id))
    .sort(byLabel);

  if (ungrouped.length > 0) {
    groups.push({
      key: "other-artists",
      label: "Other artists",
      kind: "artist",
      artists: ungrouped,
    });
  }

  const frontier = data.nodes
    .filter((node) => node.kind === "frontier")
    .sort(byLabel);

  if (frontier.length > 0) {
    groups.push({
      key: "new-to-you",
      label: "New to you",
      kind: "frontier",
      artists: frontier,
    });
  }

  return groups;
}
