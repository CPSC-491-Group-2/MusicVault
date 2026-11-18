"use client";

import { useEffect, useRef } from "react";

import { Button } from "@/components/ui/Button";
import { CloseIcon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/IconButton";
import { Surface } from "@/components/ui/Surface";
import { Tag } from "@/components/ui/Tag";

import type { TasteArtistSong, TasteNode } from "@/lib/taste";

type TasteDetailPanelProps = {
  node: TasteNode;
  songs: TasteArtistSong[] | undefined;
  related: TasteNode[];
  onDismiss: () => void;
};

export function TasteDetailPanel({
  node,
  songs,
  related,
  onDismiss,
}: TasteDetailPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    panelRef.current?.scrollIntoView({ block: "nearest" });
  }, [node.id]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onDismiss();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onDismiss]);

  return (
    <div ref={panelRef}>
      <Surface as="section" tone="paper" className="grid gap-5">
        <div className="flex items-start justify-between gap-5">
          <h3 className="text-balance text-[22px] font-semibold leading-[1.2] tracking-[-0.015em]">
            {node.kind === "tag" ? <Tag>{node.label}</Tag> : node.label}
          </h3>

          <IconButton
            size={48}
            tone="blush"
            label="Close details"
            onClick={onDismiss}
            className="shrink-0"
          >
            <CloseIcon className="h-6 w-6" />
          </IconButton>
        </div>

        {node.kind === "tag" ? (
          <ul className="grid gap-2">
            {related.map((artist) => (
              <li key={artist.id} className="text-[16px] leading-[1.5]">
                {artist.label}
              </li>
            ))}
          </ul>
        ) : null}

        {node.kind !== "tag" && songs && songs.length > 0 ? (
          <ul className="grid gap-2">
            {songs.map((song) => (
              <li
                key={song.id}
                className="text-[16px] leading-[1.5] text-olive/70"
              >
                {song.title}
                <span className="text-olive/45"> · {song.album}</span>
              </li>
            ))}
          </ul>
        ) : null}

        {node.kind !== "tag" && !songs ? (
          <p className="max-w-[60ch] text-[16px] leading-[1.5] text-olive/70">
            New to you. Nothing saved by this artist yet, so they sit next to
            the ones you already keep.
          </p>
        ) : null}

        {node.kind === "tag" ? null : (
          <Button
            href={`/swipe?seed=${encodeURIComponent(node.id)}`}
            variant="primary"
            size="md"
            className="w-fit"
          >
            Swipe more like this
          </Button>
        )}
      </Surface>
    </div>
  );
}
