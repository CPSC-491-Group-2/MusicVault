import Image from "next/image";

import {
  Button,
  CheckIcon,
  PlusIcon,
  Surface,
} from "@/components/ui";
import type { SpotifyTrack } from "@/types/api";

type SongSearchResultProps = {
  track: SpotifyTrack;
  saved: boolean;
  saving: boolean;
  onSave: (track: SpotifyTrack) => void;
};

export function SongSearchResult({
  track,
  saved,
  saving,
  onSave,
}: SongSearchResultProps) {
  const artistNames = track.artists
    .map((artist) => artist.name)
    .join(", ");

  return (
    <Surface
      as="article"
      tone="paper"
      padding="md"
      className={
        saved
          ? "outline-2 outline-green"
          : undefined
      }
    >
      <div className="flex h-full flex-col gap-5">
        <div className="flex items-center gap-4">
          {track.album.image_url ? (
            <Image
              src={track.album.image_url}
              alt={`${track.title} by ${artistNames}, album cover`}
              width={72}
              height={72}
              className="size-[72px] shrink-0 rounded-[12px] object-cover"
            />
          ) : (
            <div
              aria-hidden="true"
              className="size-[72px] shrink-0 rounded-[12px] bg-olive/14"
            />
          )}

          <div className="min-w-0">
            <h2 className="text-[22px] font-semibold leading-[1.2] tracking-[-0.015em] text-olive">
              {track.title}
            </h2>

            <p className="mt-1 text-[15px] leading-5 text-olive/70">
              {artistNames}
            </p>

            {track.album.name ? (
              <p className="mt-1 text-[13px] text-olive/70">
                {track.album.name}
              </p>
            ) : null}
          </div>
        </div>

        <div className="mt-auto">
          {saved ? (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled
              icon={
                <CheckIcon className="size-5 text-green" />
              }
            >
              Saved
            </Button>
          ) : (
            <Button
              type="button"
              variant="primary"
              size="sm"
              loading={saving}
              loadingLabel="Saving"
              icon={
                <PlusIcon className="size-5" />
              }
              onClick={() => onSave(track)}
            >
              Add to vault
            </Button>
          )}
        </div>
      </div>
    </Surface>
  );
}