"use client";

import { useState } from "react";

type Song = {
  id: number;
  title: string;
  artist: string;
};

const sampleSongs: Song[] = [
  {
    id: 1,
    title: "Lose Yourself",
    artist: "Eminem",
  },
  {
    id: 2,
    title: "Numb",
    artist: "Linkin Park",
  },
  {
    id: 3,
    title: "Everlong",
    artist: "Foo Fighters",
  },
];

export default function PreferencesPage() {
  const [preferredSongs, setPreferredSongs] = useState<Song[]>([]);
  const [songTitle, setSongTitle] = useState("");
  const [artistName, setArtistName] = useState("");
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  function addSong(song: Song) {
    const alreadyAdded = preferredSongs.some(
      (preferredSong) => preferredSong.id === song.id
    );

    if (!alreadyAdded) {
      setPreferredSongs([...preferredSongs, song]);
    }
  }

  function removeSong(songId: number) {
    setPreferredSongs(
      preferredSongs.filter((song) => song.id !== songId)
    );
  }

  function addManualSong() {
    setFormError("");
    setFormSuccess("");

    const trimmedTitle = songTitle.trim();
    const trimmedArtist = artistName.trim();

    if (!trimmedTitle) {
      setFormError("Song title is required.");
      return;
    }

    if (!trimmedArtist) {
      setFormError("Artist name is required.");
      return;
    }

    const duplicateSong = preferredSongs.some(
      (song) =>
        song.title.toLowerCase() === trimmedTitle.toLowerCase() &&
        song.artist.toLowerCase() === trimmedArtist.toLowerCase()
    );

    if (duplicateSong) {
      setFormError("This song is already in your preferred songs.");
      return;
    }

    const newSong: Song = {
      id: Date.now(),
      title: trimmedTitle,
      artist: trimmedArtist,
    };

    setPreferredSongs([...preferredSongs, newSong]);
    setSongTitle("");
    setArtistName("");
    setFormSuccess("Song added successfully.");
  }

  return (
    <main className="min-h-screen bg-canvas text-olive">
      <div className="mx-auto flex max-w-[1120px] flex-col gap-7 px-4 py-8 sm:px-7 lg:px-14">
      <header className="flex flex-col gap-3">
        <h1 className="text-[32px] font-semibold leading-[1.05] tracking-[-0.03em] text-balance sm:text-[44px]">
          Pick songs you love
        </h1>

        <p className="max-w-[65ch] text-[17px] leading-6 text-olive/70">
          Choose from your Spotify favorites or add a song yourself. We’ll use them to shape your vault.
        </p>
      </header>

        <section className="mb-10">
          <h2 className="mb-4 text-2xl font-semibold">
            Your top songs
          </h2>

          <div className="space-y-3">
            {sampleSongs.map((song) => {
              const isPreferred = preferredSongs.some(
                (preferredSong) => preferredSong.id === song.id
              );

              return (
                <div
                  key={song.id}
                  className="flex min-h-20 items-center justify-between gap-4 rounded-[20px] border border-olive/14 bg-paper px-5 py-4"                >
                  <div>
                    <p className="text-[17px] font-semibold leading-6 text-olive">{song.title}</p>
                    <p className="text-[15px] leading-5 text-olive/70">
                      {song.artist}
                    </p>
                  </div>

                  <Button
                    type="button"
                    variant={isPreferred ? "secondary" : "primary"}
                    disabled={isPreferred}
                    onClick={() => addSong(song)}
                    >
                    {isPreferred ? "Saved" : "Save to vault"}
                  </Button>
                </div>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="mb-4 text-2xl font-semibold">
            Songs in your vault
          </h2>

          {preferredSongs.length === 0 ? (
            <div className="rounded-[28px] bg-paper p-7">
              <p className="text-[18px] font-medium text-olive">
                Your vault is empty
              </p>

              <p className="mt-2 max-w-[55ch] text-[16px] leading-6 text-olive/70">
                Pick a few songs you love and they’ll show up here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {preferredSongs.map((song) => (
                <div
                  key={song.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-semibold">{song.title}</p>
                    <p className="text-sm text-gray-600">
                      {song.artist}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeSong(song.id)}
                    className="rounded border px-4 py-2"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="mt-10">
          <h2 className="mb-4 text-2xl font-semibold">
            Add a song yourself 
          </h2>

          <div className="flex flex-col gap-5 rounded-[28px] bg-paper p-7">
            <div>
              <label
                htmlFor="song-title"
                className="text-[16px] font-medium text-olive"
              >
                Song Title
              </label>

              <input
                id="song-title"
                type="text"
                value={songTitle}
                onChange={(event) => {
                setSongTitle(event.target.value);
                setFormError("");
                setFormSuccess("");
              }}
                placeholder="Enter a song title"
                className="
                min-h-12 w-full
                rounded-[18px]
                border border-olive/14
                bg-paper
                px-4 py-3
                text-[16px] text-olive
                placeholder:text-olive/45
                outline-none
                focus:border-olive
                focus:ring-2
                focus:ring-olive
                focus:ring-offset-2
                "
              />
            </div>

            <div>
              <label
                htmlFor="artist-name"
                className="mb-1 block font-medium"
              >
                Artist
              </label>

              <input
                id="artist-name"
                type="text"
                value={artistName}
                onChange={(event) => {
                  setArtistName(event.target.value);
                  setFormError("");
                  setFormSuccess("");
                }}
                className="
                  min-h-12 w-full
                  rounded-[18px]
                  border border-olive/14
                  bg-paper
                  px-4 py-3
                  text-[16px] text-olive
                  placeholder:text-olive/45
                  outline-none
                  focus:border-olive
                  focus:ring-2
                  focus:ring-olive
                  focus:ring-offset-2
                "
                placeholder="Enter artist name"
              />
            </div>

            {formError && (
              <p className="text-[15px] text-red">
                {formError}
              </p>
            )}

            {formSuccess && (
              <p className="text-[15px] font-medium text-green">
                {formSuccess}
              </p>
            )}

            <button
              type="button"
              onClick={addManualSong}
              className="rounded border px-4 py-2"
            >
              Add Song
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}