"use client";

import type { KeyboardEvent as ReactKeyboardEvent } from "react";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import {
  Button,
  CloseIcon,
  FormMessage,
  HeartIcon,
  IconButton,
  LoadingStack,
  SkipIcon,
  Surface,
} from "@/components/ui";
import {
  discoveryErrorMessage,
  getDeck,
  postSwipe,
  type DeckItem,
  type SwipeAction,
  type SwipeSong,
} from "@/lib/swipe";

import { LEAVE_MS, SwipeCard } from "./SwipeCard";

const DECK_LIMIT = 10;
const PREFETCH_AT = 3;
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";

const DECK_CLASSES =
  "mx-auto grid w-full max-w-[380px] overflow-hidden rounded-[28px] outline-offset-0 transition-[outline-offset] duration-150 ease-mv focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive";

const ANNOUNCE: Record<SwipeAction, string> = {
  keep: "Kept",
  pass: "Passed",
  skip: "Skipped",
};

const KEY_ACTIONS: Record<string, SwipeAction | undefined> = {
  ArrowRight: "keep",
  ArrowLeft: "pass",
  ArrowDown: "skip",
};

type DeckStatus = "loading" | "ready" | "error";

function subscribeMotion(onChange: () => void) {
  const query = window.matchMedia(REDUCED_MOTION);
  query.addEventListener("change", onChange);
  return () => query.removeEventListener("change", onChange);
}

function readMotion(): boolean {
  return window.matchMedia(REDUCED_MOTION).matches;
}

function readMotionOnServer(): boolean {
  return false;
}

type SwipeDeckProps = {
  seed: string | null;
  simulateFailure: boolean;
};

export function SwipeDeck({ seed, simulateFailure }: SwipeDeckProps) {
  const [items, setItems] = useState<DeckItem[]>([]);
  const [status, setStatus] = useState<DeckStatus>("loading");
  const [drained, setDrained] = useState(false);
  const [shownIds, setShownIds] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [announcement, setAnnouncement] = useState("");
  const [leaving, setLeaving] = useState<{
    id: string;
    action: SwipeAction;
  } | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const reducedMotion = useSyncExternalStore(
    subscribeMotion,
    readMotion,
    readMotionOnServer,
  );

  const audioRef = useRef<HTMLAudioElement>(null);
  const prefetching = useRef(false);
  const positions = useRef(new Map<string, number>());
  const pending = useRef<{
    id: string;
    timer: ReturnType<typeof setTimeout>;
  } | null>(null);

  useEffect(() => {
    const element = audioRef.current;

    return () => {
      element?.pause();

      if (pending.current !== null) {
        clearTimeout(pending.current.timer);
        pending.current = null;
      }
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const result = await getDeck({ limit: DECK_LIMIT, exclude: [], seed });

      if (cancelled) {
        return;
      }

      if (!result.ok) {
        setStatus("error");
        setError(discoveryErrorMessage(result.error));
        return;
      }

      positions.current = new Map(
        result.data.items.map((item, index) => [item.song.id, index]),
      );
      setItems(result.data.items);
      setShownIds(result.data.items.map((item) => item.song.id));
      setDrained(result.data.items.length === 0);
      setError("");
      setStatus("ready");
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [seed, reloadKey]);

  useEffect(() => {
    if (
      status !== "ready" ||
      drained ||
      prefetching.current ||
      items.length > PREFETCH_AT
    ) {
      return;
    }

    prefetching.current = true;
    let cancelled = false;

    async function loadMore() {
      const result = await getDeck({
        limit: DECK_LIMIT,
        exclude: shownIds,
        seed,
      });
      prefetching.current = false;

      // A failed prefetch leaves the cards already in hand alone.
      if (cancelled || !result.ok) {
        return;
      }

      if (result.data.items.length === 0) {
        setDrained(true);
        return;
      }

      result.data.items.forEach((item, index) => {
        positions.current.set(item.song.id, index);
      });

      setItems((previous) => [
        ...previous,
        ...result.data.items.filter(
          (item) => !previous.some((held) => held.song.id === item.song.id),
        ),
      ]);
      setShownIds((previous) => [
        ...previous,
        ...result.data.items
          .map((item) => item.song.id)
          .filter((id) => !previous.includes(id)),
      ]);
    }

    void loadMore();
    return () => {
      cancelled = true;
    };
  }, [status, drained, items.length, shownIds, seed]);

  function stopAudio() {
    const element = audioRef.current;

    if (element !== null) {
      element.pause();
      element.currentTime = 0;
    }

    setPlayingId(null);
  }

  function togglePlay(song: SwipeSong) {
    const element = audioRef.current;

    if (element === null || song.preview_url === null) {
      return;
    }

    if (playingId === song.id) {
      element.pause();
      setPlayingId(null);
      return;
    }

    element.src = song.preview_url;
    void element
      .play()
      .then(() => setPlayingId(song.id))
      .catch(() => setPlayingId(null));
  }

  function decide(item: DeckItem, action: SwipeAction) {
    if (leaving !== null) {
      return;
    }

    const { song } = item;

    setError("");
    setAnnouncement(`${ANNOUNCE[action]} ${song.title} by ${song.artist}`);
    stopAudio();
    setLeaving({ id: song.id, action });

    void postSwipe(
      {
        song_id: song.id,
        action,
        deck_position: positions.current.get(song.id) ?? 0,
      },
      { simulateFailure },
    ).then((result) => {
      if (result.ok) {
        return;
      }

      const scheduled = pending.current;

      if (scheduled !== null && scheduled.id === song.id) {
        clearTimeout(scheduled.timer);
        pending.current = null;
        setLeaving(null);
      }

      setItems((previous) =>
        previous.some((held) => held.song.id === song.id)
          ? previous
          : [item, ...previous],
      );
      setShownIds((previous) => previous.filter((id) => id !== song.id));
      setError(discoveryErrorMessage(result.error));
    });

    const timer = setTimeout(
      () => {
        pending.current = null;
        setLeaving(null);
        setItems((previous) =>
          previous.filter((held) => held.song.id !== song.id),
        );
      },
      reducedMotion ? 0 : LEAVE_MS,
    );

    pending.current = { id: song.id, timer };
  }

  function retry() {
    setStatus("loading");
    setError("");
    setReloadKey((key) => key + 1);
  }

  function handleKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    const top = items[0];

    if (top === undefined) {
      return;
    }

    if (event.key === " ") {
      // A focused button handles its own space key.
      if (event.target !== event.currentTarget) {
        return;
      }

      event.preventDefault();
      togglePlay(top.song);
      return;
    }

    const action = KEY_ACTIONS[event.key];

    if (action === undefined) {
      return;
    }

    event.preventDefault();
    decide(top, action);
  }

  const top = items[0];

  let body;

  if (status === "error") {
    body = (
      <Surface as="section" tone="paper" className="grid justify-items-start gap-5">
        <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
          Swipe deck unavailable
        </h2>

        <p className="max-w-[60ch] text-[17px] leading-[1.5] text-olive/70">
          {error}
        </p>

        <Button type="button" variant="secondary" size="md" onClick={retry}>
          Try again
        </Button>
      </Surface>
    );
  } else if (top === undefined) {
    body = drained ? (
      <Surface as="section" tone="paper" className="grid justify-items-start gap-5">
        <h2 className="text-balance text-[28px] font-semibold leading-[1.15] tracking-[-0.015em]">
          That is every song for now
        </h2>

        <p className="max-w-[60ch] text-[17px] leading-[1.5] text-olive/70">
          Add a few more songs to your vault and the deck fills up again.
        </p>

        <Button href="/search" variant="primary" size="md">
          Search for songs
        </Button>
      </Surface>
    ) : (
      <Surface
        as="section"
        tone="paper"
        className="grid min-h-[260px] place-items-center"
      >
        <div className="grid justify-items-center gap-4">
          <LoadingStack size={72} label="Loading songs to swipe" />

          <p className="text-[16px] text-olive/70">Picking songs for you.</p>
        </div>
      </Surface>
    );
  } else {
    body = (
      <div className="grid gap-7">
        {error ? (
          <FormMessage tone="error" className="mv-shake">
            {error}
          </FormMessage>
        ) : null}

        {/* oxlint-disable-next-line jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/prefer-tag-over-role -- the deck is one focus stop for the arrow keys */}
        <div role="group" aria-label="Song cards" tabIndex={0} onKeyDown={handleKeyDown} className={DECK_CLASSES}>
          {items.slice(0, 3).map((item, index) => (
            <SwipeCard
              key={item.song.id}
              item={item}
              depth={index}
              leaving={
                leaving !== null && leaving.id === item.song.id
                  ? leaving.action
                  : null
              }
              reducedMotion={reducedMotion}
              playing={playingId === item.song.id}
              onTogglePlay={() => togglePlay(item.song)}
              onDecide={(action) => decide(item, action)}
            />
          ))}
        </div>

        <div className="flex items-center justify-center gap-5">
          <IconButton
            size={56}
            tone="blush"
            label={`Pass on ${top.song.title}`}
            onClick={() => decide(top, "pass")}
          >
            <CloseIcon className="size-6" />
          </IconButton>

          <IconButton
            size={76}
            tone="green"
            label={`Keep ${top.song.title}`}
            onClick={() => decide(top, "keep")}
          >
            <HeartIcon className="size-8" />
          </IconButton>

          <IconButton
            size={48}
            tone="paper"
            label={`Skip ${top.song.title}`}
            onClick={() => decide(top, "skip")}
          >
            <SkipIcon className="size-5" />
          </IconButton>
        </div>

        <p className="text-center text-[13px] text-olive/70">
          Drag the card or use the arrow keys. Right keeps, left passes, down
          skips, space plays.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* oxlint-disable-next-line jsx-a11y/media-has-caption */}
      <audio
        ref={audioRef}
        preload="none"
        className="hidden"
        onEnded={() => setPlayingId(null)}
      />

      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {announcement}
      </div>

      {body}
    </div>
  );
}
