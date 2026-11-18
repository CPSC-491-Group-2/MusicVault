import Link from "next/link";

import { Surface } from "@/components/ui/Surface";
import { Tag } from "@/components/ui/Tag";

import type { TasteArtistDetail, TasteNode } from "@/lib/taste";

import type { TasteListGroup } from "./graph-data";

const ARTIST_LINK_CLASSES =
  "inline-flex min-h-[44px] w-fit items-center rounded-[10px] text-[17px] font-medium underline-offset-4 outline-offset-0 transition-[outline-offset] duration-150 ease-mv hover:underline focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-olive";

type TasteListProps = {
  groups: TasteListGroup[];
  artists: Record<string, TasteArtistDetail>;
};

export function TasteList({ groups, artists }: TasteListProps) {
  return (
    <div className="grid gap-6">
      {groups.map((group) => (
        <Surface key={group.key} as="section" tone="paper" className="grid gap-5">
          <h3 className="text-balance text-[22px] font-semibold leading-[1.2] tracking-[-0.015em]">
            {group.kind === "tag" ? <Tag>{group.label}</Tag> : group.label}
          </h3>

          {group.kind === "frontier" ? (
            <p className="max-w-[60ch] text-[16px] leading-[1.5] text-olive/70">
              Nothing saved by these yet. They sit next to the artists you
              already keep.
            </p>
          ) : null}

          <ul className="grid gap-5">
            {group.artists.map((artist) => (
              <ArtistItem
                key={artist.id}
                artist={artist}
                detail={artists[artist.id] as TasteArtistDetail | undefined}
              />
            ))}
          </ul>
        </Surface>
      ))}
    </div>
  );
}

function ArtistItem({
  artist,
  detail,
}: {
  artist: TasteNode;
  detail: TasteArtistDetail | undefined;
}) {
  return (
    <li className="grid gap-1">
      <Link
        href={`/swipe?seed=${encodeURIComponent(artist.id)}`}
        className={ARTIST_LINK_CLASSES}
      >
        {artist.label}
      </Link>

      {detail ? (
        <ul className="grid gap-1">
          {detail.songs.map((song) => (
            <li
              key={song.id}
              className="text-[15px] leading-[1.45] text-olive/70"
            >
              {song.title}
              <span className="text-olive/45"> · {song.album}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </li>
  );
}
