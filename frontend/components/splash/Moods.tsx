"use client";

import Image from "next/image";
import { useState } from "react";

import { Chip } from "@/components/ui/Chip";

const MOODS = [
  "Late-night drive",
  "Rainy afternoon",
  "Cooking for friends",
  "Focus",
  "Sunday morning",
  "Gym",
  "Heartbroken",
  "Road trip",
  "Slow dancing",
  "Cleaning the apartment",
  "Walking home",
];

const INITIALLY_SELECTED = ["Late-night drive", "Focus", "Slow dancing"];

export default function Moods() {
  // Selection is local only on purpose: nothing about it persists yet.
  const [selected, setSelected] = useState(() => new Set(INITIALLY_SELECTED));

  function toggle(mood: string) {
    setSelected((current) => {
      const next = new Set(current);

      if (next.has(mood)) {
        next.delete(mood);
      } else {
        next.add(mood);
      }

      return next;
    });
  }

  return (
    <section className="mx-auto w-full max-w-[1440px] px-4 pb-32 lg:px-16">
      <Image
        src="/images/splash/moods.jpg"
        alt="Someone lying back with their feet up next to a boombox"
        width={2624}
        height={1100}
        className="aspect-[4/3] w-full rounded-[20px] object-cover lg:aspect-auto lg:h-[550px]"
      />

      <div className="mt-14 flex flex-col gap-20 lg:flex-row">
        <div className="lg:w-[480px] lg:shrink-0">
          <h2 className="text-[44px] font-semibold tracking-[-0.025em]">
            Start with a feeling
          </h2>

          <p className="mt-4 text-[18px]">
            Pick a few moods. We&apos;ll use them alongside your listening
            history to steer what you hear first.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          {MOODS.map((mood) => (
            <Chip
              key={mood}
              pressed={selected.has(mood)}
              onPressedChange={() => toggle(mood)}
            >
              {mood}
            </Chip>
          ))}
        </div>
      </div>
    </section>
  );
}
