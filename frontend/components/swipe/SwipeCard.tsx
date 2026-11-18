"use client";

import Image from "next/image";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import { useRef, useState } from "react";

import { IconButton, PauseIcon, PlayIcon, Surface } from "@/components/ui";
import type { DeckItem, SwipeAction } from "@/lib/swipe";

export const LEAVE_MS = 250;

const COMMIT_DISTANCE = 120;
const FLICK_DISTANCE = 48;
const FLICK_VELOCITY = 0.5;
const TILT_PER_PX = 0.06;
const MAX_TILT = 8;
const LEAVE_DISTANCE = 520;

// Offsets must beat what origin-top scaling trims, or the peeks hide behind the top card.
const DEPTH_CLASSES = [
  "z-30 touch-none select-none",
  "pointer-events-none z-20 origin-top translate-y-6 scale-[0.98] opacity-70",
  "pointer-events-none z-10 origin-top translate-y-12 scale-[0.96] opacity-45",
];

function albumInitials(album: string): string {
  return album
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => (word[0] ?? "").toUpperCase())
    .join("");
}

function clampTilt(value: number): number {
  return Math.max(-MAX_TILT, Math.min(MAX_TILT, value));
}

function leaveStyle(
  action: SwipeAction,
  reducedMotion: boolean,
): CSSProperties {
  if (reducedMotion) {
    return { opacity: 0 };
  }

  if (action === "skip") {
    return { transform: `translateY(${LEAVE_DISTANCE}px)`, opacity: 0 };
  }

  const direction = action === "keep" ? 1 : -1;

  return {
    transform: `translateX(${direction * LEAVE_DISTANCE}px) rotate(${direction * MAX_TILT}deg)`,
    opacity: 0,
  };
}

function motionClasses(dragging: boolean, leaving: boolean): string {
  if (dragging) {
    return "transition-none";
  }

  if (leaving) {
    return "transition-[transform,opacity] duration-[250ms] ease-mv";
  }

  return "transition-transform duration-[250ms] ease-mv";
}

type SwipeCardProps = {
  item: DeckItem;
  depth: number;
  leaving: SwipeAction | null;
  reducedMotion: boolean;
  playing: boolean;
  onTogglePlay: () => void;
  onDecide: (action: SwipeAction) => void;
};

export function SwipeCard({
  item,
  depth,
  leaving,
  reducedMotion,
  playing,
  onTogglePlay,
  onDecide,
}: SwipeCardProps) {
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const start = useRef({ x: 0, time: 0 });

  const { song } = item;
  const top = depth === 0;
  const hasPreview = song.preview_url !== null;

  function handlePointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (!top || leaving !== null || event.button !== 0) {
      return;
    }

    // Capturing the pointer would swallow the preview button's click.
    if ((event.target as HTMLElement).closest("button") !== null) {
      return;
    }

    event.currentTarget.setPointerCapture(event.pointerId);
    start.current = { x: event.clientX, time: event.timeStamp };
    setDragging(true);
  }

  function handlePointerMove(event: ReactPointerEvent<HTMLDivElement>) {
    if (!dragging) {
      return;
    }

    setDx(event.clientX - start.current.x);
  }

  function handlePointerUp(event: ReactPointerEvent<HTMLDivElement>) {
    if (!dragging) {
      return;
    }

    setDragging(false);

    const distance = event.clientX - start.current.x;
    const travelled = Math.abs(distance);
    const elapsed = Math.max(1, event.timeStamp - start.current.time);
    const flicked =
      travelled > FLICK_DISTANCE && travelled / elapsed > FLICK_VELOCITY;

    if (travelled > COMMIT_DISTANCE || flicked) {
      onDecide(distance > 0 ? "keep" : "pass");
      return;
    }

    setDx(0);
  }

  function handlePointerCancel() {
    setDragging(false);
    setDx(0);
  }

  const dragged = dragging || dx !== 0;
  const tilt = reducedMotion ? 0 : clampTilt(dx * TILT_PER_PX);

  /* Drag and leave transforms are per-pointer values, so no static class fits. */
  let style: CSSProperties | undefined;
  if (leaving !== null) {
    style = leaveStyle(leaving, reducedMotion);
  } else if (dragged) {
    style = { transform: `translateX(${dx}px) rotate(${tilt}deg)` };
  }

  const previewLabel = hasPreview
    ? `${playing ? "Pause" : "Play"} preview of ${song.title}`
    : `No preview for ${song.title}`;

  let previewText = "No preview";
  if (hasPreview) {
    previewText = playing ? "Playing" : "Preview";
  }

  return (
    <div
      aria-hidden={top ? undefined : "true"}
      className={`col-start-1 row-start-1 ${DEPTH_CLASSES[depth] ?? ""} ${motionClasses(dragging, leaving !== null)}`}
      style={style}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerCancel}
    >
      <Surface
        as="article"
        tone="paper"
        padding="md"
        className="grid h-full content-start gap-5"
      >
        {song.album_image_url === null ? (
          <div
            aria-hidden="true"
            className="grid aspect-square w-full place-items-center rounded-[20px] bg-blush"
          >
            <span className="text-[28px] font-semibold tracking-[-0.015em] text-olive">
              {albumInitials(song.album)}
            </span>
          </div>
        ) : (
          <Image
            src={song.album_image_url}
            alt={`${song.title} by ${song.artist}, album cover`}
            width={320}
            height={320}
            draggable={false}
            className="aspect-square w-full rounded-[20px] object-cover"
          />
        )}

        <div className="grid gap-1">
          <h2 className="text-balance text-[22px] font-semibold leading-[1.2] tracking-[-0.015em] text-olive">
            {song.title}
          </h2>

          <p className="text-[17px] leading-[1.5] text-olive/70">
            {song.artist}
          </p>

          <p className="text-[13px] text-olive/70">{song.album}</p>
        </div>

        <p className="text-[15px] leading-[1.45] text-olive/70">
          {item.reason.text}
        </p>

        {top ? (
          <div className="flex items-center gap-4">
            <IconButton
              size={48}
              tone="blush"
              label={previewLabel}
              disabled={!hasPreview}
              className="disabled:text-olive/45"
              onClick={onTogglePlay}
            >
              {playing ? (
                <PauseIcon className="size-6" />
              ) : (
                <PlayIcon className="size-6" />
              )}
            </IconButton>

            <span
              className={`text-[15px] ${hasPreview ? "text-olive/70" : "text-olive/45"}`}
            >
              {previewText}
            </span>
          </div>
        ) : null}
      </Surface>
    </div>
  );
}
