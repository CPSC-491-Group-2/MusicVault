import Image from "next/image";

import { POPULARITY_ROW } from "@/data/popularity-row";

// Overlay type and padding shrink as the tiles do. The smallest tiles have no
// room for three pieces of information, so they drop the artist -- the image
// alt still carries the full title and artist, so the accessible name of every
// tile stays the same regardless of which tier it falls into.
const TIERS = {
  // 280, 224, 178, 142
  large: {
    padding: "p-3",
    title: "text-[16px]",
    meta: "text-[13px]",
    showArtist: true,
  },
  // 114, 92, 76
  medium: {
    padding: "p-2",
    title: "text-[12px]",
    meta: "text-[10px]",
    showArtist: true,
  },
  // 62, 52
  small: {
    padding: "p-1.5",
    title: "text-[12px]",
    meta: "text-[10px]",
    showArtist: false,
  },
} as const;

type Tile = {
  px: number;
  box: string;
  radius: string;
  tier: keyof typeof TIERS;
};

// Tile sizes, left to right: 280 224 178 142 114 92 76 62 52. Size is the whole
// argument of this section -- it encodes play count -- so each tile is matched
// to POPULARITY_ROW by index, and this array MUST stay the same length as that
// one.
//
// The w-/h- utilities are spelled out as literal strings because Tailwind only
// generates classes it can find as static text; a template literal such as
// w-[${px}px] scans as nothing and compiles to no CSS at all.
const TILES: readonly Tile[] = [
  { px: 280, box: "w-[280px] h-[280px]", radius: "rounded-lg", tier: "large" },
  { px: 224, box: "w-[224px] h-[224px]", radius: "rounded-lg", tier: "large" },
  { px: 178, box: "w-[178px] h-[178px]", radius: "rounded-lg", tier: "large" },
  { px: 142, box: "w-[142px] h-[142px]", radius: "rounded-lg", tier: "large" },
  { px: 114, box: "w-[114px] h-[114px]", radius: "rounded-lg", tier: "medium" },
  { px: 92, box: "w-[92px] h-[92px]", radius: "rounded", tier: "medium" },
  { px: 76, box: "w-[76px] h-[76px]", radius: "rounded", tier: "medium" },
  { px: 62, box: "w-[62px] h-[62px]", radius: "rounded", tier: "small" },
  { px: 52, box: "w-[52px] h-[52px]", radius: "rounded", tier: "small" },
];

// Nine album covers in one bottom-aligned row, shrinking left to right, from a
// 5.6B-play hit down to a song with four thousand plays. The tiles carry no
// visible heading, so the section is labelled by a screen-reader-only h2.
export default function PopularityRow() {
  return (
    <section aria-labelledby="popularity-heading" className="pb-32">
      <div className="mx-auto w-full max-w-[1440px] px-4 lg:px-16">
        <h2 id="popularity-heading" className="sr-only">
          What you play most, and what we find for you
        </h2>

        {/*
          The nine tiles plus their eight 10px gaps measure a fixed 1300px, which
          only fits once the content box reaches 1300px -- at a viewport of
          1428px, given the 64px side padding. Below that the row stays a
          horizontal scroll strip at the same tile sizes. Breaking the strip out
          of the page padding and restoring it inside keeps the overflow on the
          strip and off the document, so the page itself never scrolls sideways.
        */}
        <div className="-mx-4 flex snap-x items-end gap-2.5 overflow-x-auto px-4 lg:-mx-16 lg:px-16 min-[1428px]:mx-0 min-[1428px]:overflow-visible min-[1428px]:px-0">
          {/* TODO: swap to live data */}
          {POPULARITY_ROW.map((track, index) => {
            const tile = TILES[index];
            const tier = TIERS[tile.tier];

            return (
              <a
                key={track.spotifyTrackId}
                href={`https://open.spotify.com/track/${track.spotifyTrackId}`}
                target="_blank"
                rel="noopener"
                className={`group relative shrink-0 snap-start overflow-hidden ${tile.box} ${tile.radius} focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive`}
              >
                {/*
                  No sizes prop on purpose. The tile is the same fixed pixel size
                  at every breakpoint, so Next's default for a numeric width --
                  a two-candidate srcset of width and width*2 with x descriptors
                  -- is already the minimum. Passing a pixel-only sizes value
                  would instead opt into the full deviceSizes ladder with w
                  descriptors (see next/dist/shared/lib/get-img-props.js, where
                  a sizes string containing no vw unit returns every size).
                */}
                <Image
                  src={track.coverUrl}
                  alt={`${track.title} by ${track.artist}, album cover`}
                  width={tile.px}
                  height={tile.px}
                  className="h-full w-full object-cover"
                />

                {/*
                  Revealed by mouse hover and by keyboard focus, via the group on
                  the link itself. Opacity only -- never transform, so the row's
                  size relationships never wobble.
                */}
                <span
                  className={`absolute inset-0 flex flex-col justify-end bg-olive/82 opacity-0 transition-opacity duration-150 group-hover:opacity-100 group-focus-visible:opacity-100 motion-reduce:transition-none ${tier.padding}`}
                >
                  <span className={`line-clamp-2 font-medium text-blush ${tier.title}`}>
                    {track.title}
                  </span>
                  <span className={`line-clamp-1 text-blush/75 ${tier.meta}`}>
                    {tier.showArtist
                      ? `${track.artist}, ${track.playsLabel}`
                      : track.playsLabel}
                  </span>
                </span>
              </a>
            );
          })}
        </div>

        <div className="mt-4 flex justify-between text-[15px] text-olive/75">
          <span>What you play most</span>
          <span>What we find for you</span>
        </div>
      </div>
    </section>
  );
}
