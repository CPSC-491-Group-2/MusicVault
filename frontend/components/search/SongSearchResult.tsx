import Image from "next/image";

import { Button, Surface } from "@/components/ui";
import type { SpotifyTrack } from "@/types/api";

type SongSearchResultProps = {
  track: SpotifyTrack;
  onSave: (track: SpotifyTrack) => void;
  saving?: boolean;
};

export function SongSearchResult({
  track,
  onSave,
  saving = false,
}: SongSearchResultProps) {
  const artistNames = track.artists
    .map((artist) => artist.name)
    .join(", ");

  return (
    <Surface as="article" tone="paper" padding="md">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
        <div className="flex min-w-0 flex-1 items-center gap-4">
          {track.album.image_url ? (
            <Image
              src={track.album.image_url}
              alt={`${track.title} by ${artistNames}, album cover`}
              width={64}
              height={64}
              className="size-16 shrink-0 rounded-[12px]"
            />
          ) : (
            <div
              aria-hidden="true"
              className="size-16 shrink-0 rounded-[12px] bg-olive/14"
            />
          )}

          <div className="min-w-0">
            <h2 className="text-[22px] font-semibold leading-[1.2] tracking-[-0.015em] text-olive">
              {track.title}
            </h2>

            <p className="mt-1 text-[15px] leading-5 text-olive/70">
              {artistNames}
            </p>

            {track.album.name && (
              <p className="mt-1 text-[13px] text-olive/45">
                {track.album.name}
              </p>
            )}
          </div>
        </div>

        <Button
          type="button"
          variant="primary"
          size="sm"
          loading={saving}
          loadingLabel="Saving"
          onClick={() => onSave(track)}
        >
          Save to vault
        </Button>
      </div>
    </Surface>
  );
}