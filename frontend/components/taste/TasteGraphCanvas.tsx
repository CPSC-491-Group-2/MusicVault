"use client";

import dynamic from "next/dynamic";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import type {
  ForceGraphMethods,
  LinkObject,
  NodeObject,
} from "react-force-graph-2d";

import type { TasteEdge, TasteNode } from "@/lib/taste";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

const ARTIST_RADIUS_BASE = 4.5;
const ARTIST_RADIUS_SCALE = 1.6;
const TAG_RADIUS_BASE = 3;
const TAG_RADIUS_SCALE = 0.6;
const FRONTIER_RADIUS = 5;
const FRONTIER_STROKE_PX = 1.5;
const POINTER_PADDING = 4;

const LABEL_ZOOM = 1.8;
const LABEL_SIZE_PX = 12;
const LABEL_GAP_PX = 6;

const DIM_ALPHA = 0.18;
const LINK_ALPHA = 0.4;
const LINK_ALPHA_ACTIVE = 0.7;
const LINK_ALPHA_DIM = 0.08;
const LINK_WIDTH = 0.8;
const LINK_WIDTH_ACTIVE = 1.8;

const WARMUP_TICKS = 20;
const COOLDOWN_TICKS = 200;
const WARMUP_TICKS_STILL = 200;
const COOLDOWN_TICKS_STILL = 0;

const FIT_PADDING = 28;
const FIT_MS = 250;
const MIN_ZOOM = 0.4;
const MAX_ZOOM = 8;

const MIN_HEIGHT = 320;
const MAX_HEIGHT = 560;
const HEIGHT_RATIO = 0.72;

const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";

type Rgb = { r: number; g: number; b: number };

type Palette = { olive: Rgb; orchid: Rgb; font: string };

type TasteGraphNode = TasteNode & { x?: number; y?: number };

type TasteGraphCanvasProps = {
  nodes: TasteNode[];
  edges: TasteEdge[];
  neighbors: Map<string, Set<string>>;
  onSelect: (id: string) => void;
};

function parseColor(value: string): Rgb | null {
  const hex = value.trim().replace("#", "");
  const full = hex.length === 3 ? hex.replace(/./g, (part) => part + part) : hex;

  if (!/^[0-9a-fA-F]{6}$/.test(full)) {
    return null;
  }

  const parsed = Number.parseInt(full, 16);

  return {
    r: (parsed >> 16) & 255,
    g: (parsed >> 8) & 255,
    b: parsed & 255,
  };
}

let cached: Palette | null = null;

/* The canvas cannot read Tailwind classes, so the palette comes from the theme variables. */
function palette(): Palette | null {
  if (cached) {
    return cached;
  }

  const styles = getComputedStyle(document.documentElement);
  const olive = parseColor(styles.getPropertyValue("--color-olive"));
  const orchid = parseColor(styles.getPropertyValue("--color-orchid"));

  if (!olive || !orchid) {
    return null;
  }

  cached = { olive, orchid, font: getComputedStyle(document.body).fontFamily };
  return cached;
}

function subscribeStill(onChange: () => void): () => void {
  const query = window.matchMedia(REDUCED_MOTION);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

function readStill(): boolean {
  return window.matchMedia(REDUCED_MOTION).matches;
}

function readStillOnServer(): boolean {
  return false;
}

function rgba(color: Rgb, alpha: number): string {
  return `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
}

function nodeRadius(node: TasteNode): number {
  if (node.kind === "tag") {
    return TAG_RADIUS_BASE + TAG_RADIUS_SCALE * Math.sqrt(node.weight);
  }

  if (node.kind === "frontier") {
    return FRONTIER_RADIUS;
  }

  return ARTIST_RADIUS_BASE + ARTIST_RADIUS_SCALE * Math.sqrt(node.weight);
}

function endpointId(endpoint: unknown): string | null {
  if (typeof endpoint === "string") {
    return endpoint;
  }

  if (endpoint !== null && typeof endpoint === "object" && "id" in endpoint) {
    return String((endpoint as { id: unknown }).id);
  }

  return null;
}

export function TasteGraphCanvas({
  nodes,
  edges,
  neighbors,
  onSelect,
}: TasteGraphCanvasProps) {
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined);
  const wrapRef = useRef<HTMLDivElement>(null);
  const hoverRef = useRef<string | null>(null);
  const fittedRef = useRef(false);

  const [size, setSize] = useState<{ width: number; height: number } | null>(
    null,
  );

  const still = useSyncExternalStore(
    subscribeStill,
    readStill,
    readStillOnServer,
  );

  useEffect(() => {
    const element = wrapRef.current;
    if (!element) {
      return;
    }

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) {
        return;
      }

      const width = Math.floor(entry.contentRect.width);
      const height = Math.round(
        Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, width * HEIGHT_RATIO)),
      );

      setSize((previous) =>
        previous && previous.width === width && previous.height === height
          ? previous
          : { width, height },
      );
    });

    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!size || !fittedRef.current) {
      return;
    }

    graphRef.current?.zoomToFit(still ? 0 : FIT_MS, FIT_PADDING);
  }, [size, still]);

  const graphData = useMemo(
    () => ({
      nodes: nodes.map((node) => ({ ...node })),
      links: edges.map((edge) => ({ source: edge.src, target: edge.dst })),
    }),
    [nodes, edges],
  );

  const isActive = useCallback(
    (id: string) => {
      const hovered = hoverRef.current;

      return (
        hovered === null ||
        hovered === id ||
        neighbors.get(hovered)?.has(id) === true
      );
    },
    [neighbors],
  );

  const paintNode = useCallback(
    (
      node: NodeObject,
      ctx: CanvasRenderingContext2D,
      globalScale: number,
    ) => {
      const taste = node as TasteGraphNode;
      const colors = palette();
      if (!colors || taste.x === undefined || taste.y === undefined) {
        return;
      }

      const radius = nodeRadius(taste);
      const active = isActive(taste.id);
      ctx.globalAlpha = active ? 1 : DIM_ALPHA;

      ctx.beginPath();
      ctx.arc(taste.x, taste.y, radius, 0, Math.PI * 2);

      if (taste.kind === "frontier") {
        ctx.lineWidth = FRONTIER_STROKE_PX / globalScale;
        ctx.strokeStyle = rgba(colors.olive, 1);
        ctx.stroke();
      } else {
        ctx.fillStyle = rgba(
          taste.kind === "tag" ? colors.orchid : colors.olive,
          1,
        );
        ctx.fill();
      }

      const hovered = hoverRef.current;
      const near = hovered !== null && active;

      if (near || globalScale > LABEL_ZOOM) {
        ctx.font = `${LABEL_SIZE_PX / globalScale}px ${colors.font}`;
        ctx.fillStyle = rgba(colors.olive, 1);
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(
          taste.label,
          taste.x,
          taste.y + radius + LABEL_GAP_PX / globalScale,
        );
      }

      ctx.globalAlpha = 1;
    },
    [isActive],
  );

  const paintPointerArea = useCallback(
    (node: NodeObject, color: string, ctx: CanvasRenderingContext2D) => {
      const taste = node as TasteGraphNode;
      if (taste.x === undefined || taste.y === undefined) {
        return;
      }

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(
        taste.x,
        taste.y,
        nodeRadius(taste) + POINTER_PADDING,
        0,
        Math.PI * 2,
      );
      ctx.fill();
    },
    [],
  );

  const isIncident = useCallback((link: LinkObject) => {
    const hovered = hoverRef.current;

    return (
      endpointId(link.source) === hovered || endpointId(link.target) === hovered
    );
  }, []);

  const linkColor = useCallback(
    (link: LinkObject) => {
      const colors = palette();
      if (!colors) {
        return "transparent";
      }

      if (hoverRef.current === null) {
        return rgba(colors.olive, LINK_ALPHA);
      }

      return rgba(
        colors.olive,
        isIncident(link) ? LINK_ALPHA_ACTIVE : LINK_ALPHA_DIM,
      );
    },
    [isIncident],
  );

  const linkWidth = useCallback(
    (link: LinkObject) =>
      hoverRef.current !== null && isIncident(link)
        ? LINK_WIDTH_ACTIVE
        : LINK_WIDTH,
    [isIncident],
  );

  /* Painting reads the ref, so a hover never has to re-render React. */
  const handleHover = useCallback((node: NodeObject | null) => {
    hoverRef.current = node ? String(node.id) : null;
  }, []);

  const handleClick = useCallback(
    (node: NodeObject) => {
      onSelect(String(node.id));
    },
    [onSelect],
  );

  const handleEngineStop = useCallback(() => {
    if (fittedRef.current) {
      return;
    }

    fittedRef.current = true;
    graphRef.current?.zoomToFit(still ? 0 : FIT_MS, FIT_PADDING);
  }, [still]);

  return (
    <div
      ref={wrapRef}
      // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role
      role="img"
      aria-label="Map of the artists and tags in your taste, and the links between them. The list view has the same artists, tags and songs as text."
      className="w-full overflow-hidden rounded-[20px]"
      style={{ height: size?.height ?? MIN_HEIGHT }}
    >
      {size ? (
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          width={size.width}
          height={size.height}
          autoPauseRedraw={false}
          nodeCanvasObjectMode={() => "replace"}
          nodeCanvasObject={paintNode}
          nodePointerAreaPaint={paintPointerArea}
          linkColor={linkColor}
          linkWidth={linkWidth}
          minZoom={MIN_ZOOM}
          maxZoom={MAX_ZOOM}
          warmupTicks={still ? WARMUP_TICKS_STILL : WARMUP_TICKS}
          cooldownTicks={still ? COOLDOWN_TICKS_STILL : COOLDOWN_TICKS}
          onNodeHover={handleHover}
          onNodeClick={handleClick}
          onEngineStop={handleEngineStop}
        />
      ) : null}
    </div>
  );
}
