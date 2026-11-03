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
    <main className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl">
        <h1 className="mb-2 text-3xl font-bold">
          Preferred Songs
        </h1>

        <p className="mb-8 text-gray-600">
          Select songs you like or add a song manually.
        </p>

        <section className="mb-10">
          <h2 className="mb-4 text-2xl font-semibold">
            Your Top Songs
          </h2>

          <div className="space-y-3">
            {sampleSongs.map((song) => {
              const isPreferred = preferredSongs.some(
                (preferredSong) => preferredSong.id === song.id
              );

              return (
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
                    disabled={isPreferred}
                    onClick={() => addSong(song)}
                    className="rounded border px-4 py-2 disabled:opacity-50"
                  >
                    {isPreferred ? "Added" : "Add"}
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="mb-4 text-2xl font-semibold">
            Your Preferred Songs
          </h2>

          {preferredSongs.length === 0 ? (
            <p className="text-gray-600">
              No preferred songs selected yet.
            </p>
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
            Add a Song Manually
          </h2>

          <div className="space-y-4 rounded-lg border p-4">
            <div>
              <label
                htmlFor="song-title"
                className="mb-1 block font-medium"
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
                className="w-full rounded border px-3 py-2"
                placeholder="Enter song title"
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
                className="w-full rounded border px-3 py-2"
                placeholder="Enter artist name"
              />
            </div>

            {formError && (
              <p className="text-sm text-red-600">
                {formError}
              </p>
            )}

            {formSuccess && (
              <p className="text-sm text-green-600">
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