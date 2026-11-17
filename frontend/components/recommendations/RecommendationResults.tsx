"use client";

import { useEffect, useState } from "react";

import { LoadingStack } from "@/components/ui/LoadingStack";
import { Surface } from "@/components/ui/Surface";

import {
  getRecommendations,
  type RecommendationResult,
} from "@/lib/recommendations";

import type {
  RecommendationItem,
} from "@/types/api";


function recommendationErrorMessage(
  result: RecommendationResult,
): string {
  if (result.ok) {
    return "";
  }

  switch (result.error) {
    case "unauthorized":
      return "Sign in to view recommendations.";

    case "service_unavailable":
      return "Recommendations are temporarily unavailable.";

    default:
      return "We couldn't load recommendations. Try again.";
  }
}


function formatMatch(score: number): string {
  return `${Math.round(score * 100)}% match`;
}


export function RecommendationResults() {
  const [items, setItems] =
    useState<RecommendationItem[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    async function loadRecommendations() {
      setLoading(true);
      setError("");

      const result = await getRecommendations();

      setLoading(false);

      if (!result.ok) {
        setItems([]);
        setError(
          recommendationErrorMessage(result),
        );
        return;
      }

      setItems(result.data.items);
    }

    void loadRecommendations();
  }, []);


  if (loading) {
    return (
      <Surface
        as="section"
        tone="paper"
        className="grid min-h-[260px] place-items-center"
      >
        <div className="grid justify-items-center gap-4">
          <LoadingStack
            size={72}
            label="Loading recommendations"
          />

          <p className="text-[16px] text-olive/70">
            Finding music for you...
          </p>
        </div>
      </Surface>
    );
  }


  if (error) {
    return (
      <Surface
        as="section"
        tone="paper"
        className="grid gap-3"
      >
        <h2 className="text-[24px] font-semibold">
          Recommendations unavailable
        </h2>

        <p className="text-[16px] leading-6 text-olive/70">
          {error}
        </p>
      </Surface>
    );
  }


  if (items.length === 0) {
    return (
      <Surface
        as="section"
        tone="dashed"
        className="grid gap-3"
      >
        <h2 className="text-[24px] font-semibold">
          No recommendations yet
        </h2>

        <p className="max-w-[60ch] text-[16px] leading-6 text-olive/70">
          Add or connect some music preferences first so MusicVault
          has enough information to generate personalized results.
        </p>
      </Surface>
    );
  }


  return (
    <section
      aria-label="Recommendation results"
      className="grid gap-5"
    >
      <div>
        <h2 className="text-[28px] font-semibold tracking-[-0.02em]">
          Recommended for you
        </h2>

        <p className="mt-2 text-[16px] text-olive/70">
          Ranked from your MusicVault listening preferences.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {items.map((item) => (
          <RecommendationCard
            key={item.id}
            item={item}
          />
        ))}
      </div>
    </section>
  );
}


function RecommendationCard({
  item,
}: {
  item: RecommendationItem;
}) {
  return (
    <Surface
      as="article"
      tone="paper"
      className="grid gap-4"
    >
      <div className="grid gap-1">
        <h3 className="text-[21px] font-semibold">
          {item.title}
        </h3>

        <p className="text-[16px] text-olive/75">
          {item.artist}
        </p>

        {item.album ? (
          <p className="text-[14px] text-olive/55">
            {item.album}
          </p>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full bg-orchid px-3 py-1 text-[14px] font-medium text-olive">
          {formatMatch(item.score)}
        </span>

        {item.reason ? (
          <span className="text-[14px] text-olive/60">
            Strongest match: {item.reason}
          </span>
        ) : null}
      </div>

      {item.popularity !== null ? (
        <p className="text-[14px] text-olive/60">
          Spotify popularity: {item.popularity}/100
        </p>
      ) : null}

      {item.spotify_url ? (
        <a
          href={item.spotify_url}
          target="_blank"
          rel="noreferrer"
          className="w-fit text-[15px] font-medium underline underline-offset-4"
        >
          Open in Spotify
        </a>
      ) : null}
    </Surface>
  );
}