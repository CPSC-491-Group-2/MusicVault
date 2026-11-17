"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { LoadingStack } from "@/components/ui/LoadingStack";
import { Surface } from "@/components/ui/Surface";

import {
  getTasteGraph,
  tasteErrorMessage,
  type TasteArtistDetail,
  type TasteGraphResponse,
} from "@/lib/taste";

import { buildGroups, buildIndex, neighborArtists } from "./graph-data";
import { TasteDetailPanel } from "./TasteDetailPanel";
import { TasteGraphCanvas } from "./TasteGraphCanvas";
import { TasteList } from "./TasteList";

const GRAPH_LIMIT = 150;

type View = "graph" | "list";

export function TasteGraphPanel() {
  const [data, setData] = useState<TasteGraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [view, setView] = useState<View>("graph");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    async function loadGraph() {
      const result = await getTasteGraph({ limit: GRAPH_LIMIT });

      setLoading(false);

      if (!result.ok) {
        setError(tasteErrorMessage(result.error));
        return;
      }

      setData(result.data);
    }

    void loadGraph();
  }, []);

  const index = useMemo(
    () => (data ? buildIndex(data.nodes, data.edges) : null),
    [data],
  );

  const groups = useMemo(
    () => (data && index ? buildGroups(data, index) : []),
    [data, index],
  );

  const handleView = useCallback((next: View) => {
    setView(next);
    setSelectedId(null);
  }, []);

  const handleDismiss = useCallback(() => setSelectedId(null), []);

  if (loading) {
    return (
      <Surface
        as="section"
        tone="paper"
        className="grid min-h-[260px] place-items-center"
      >
        <LoadingStack size={72} label="Loading your taste graph" />
      </Surface>
    );
  }

  if (error) {
    return (
      <Surface as="section" tone="paper" className="grid gap-3">
        <h2 className="text-[24px] font-semibold">Taste graph unavailable</h2>

        <p className="max-w-[60ch] text-[16px] leading-[1.5] text-olive/70">
          {error}
        </p>
      </Surface>
    );
  }

  if (!data || !index || data.nodes.length === 0) {
    return (
      <Surface as="section" tone="dashed" className="grid gap-3">
        <h2 className="text-[24px] font-semibold">No taste graph yet</h2>

        <p className="max-w-[60ch] text-[16px] leading-[1.5] text-olive/70">
          Save a few songs you love, then come back to see how your artists
          connect.
        </p>
      </Surface>
    );
  }

  const selected =
    selectedId === null ? null : (index.nodeById.get(selectedId) ?? null);

  const detail =
    selected === null
      ? undefined
      : (data.artists[selected.id] as TasteArtistDetail | undefined);

  const related =
    selected === null || selected.kind !== "tag"
      ? []
      : neighborArtists(index, selected.id);

  return (
    <div className="grid gap-7">
      <div className="flex flex-wrap items-center justify-between gap-5">
        <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
          How your taste connects
        </h2>

        <ViewToggle view={view} onChange={handleView} />
      </div>

      {view === "graph" ? (
        <>
          <Surface tone="paper">
            <TasteGraphCanvas
              nodes={data.nodes}
              edges={data.edges}
              neighbors={index.neighbors}
              onSelect={setSelectedId}
            />
          </Surface>

          {selected ? (
            <TasteDetailPanel
              node={selected}
              songs={detail?.songs}
              related={related}
              onDismiss={handleDismiss}
            />
          ) : null}
        </>
      ) : (
        <TasteList groups={groups} artists={data.artists} />
      )}
    </div>
  );
}

function ViewToggle({
  view,
  onChange,
}: {
  view: View;
  onChange: (next: View) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant={view === "graph" ? "primary" : "secondary"}
        size="md"
        aria-pressed={view === "graph"}
        onClick={() => onChange("graph")}
      >
        Graph
      </Button>

      <Button
        variant={view === "list" ? "primary" : "secondary"}
        size="md"
        aria-pressed={view === "list"}
        onClick={() => onChange("list")}
      >
        List
      </Button>
    </div>
  );
}
