// Hardcoded snapshots of real Spotify play counts, read off each track's public
// Spotify page on the date in `asOf`. Replace this array with live data once the
// backend exposes a logged-out track stats route.
//
// Note: the Spotify Web API does not return play counts at all -- only a 0-100
// `popularity` score and artist follower counts -- so `plays` cannot be filled
// from the API as-is. There is deliberately no `popularity` field here because
// we have no value to put in it.
//
// The array MUST stay sorted descending by `plays`. The popularity row sizes
// each tile by its index, so a mis-sorted array silently breaks the whole idea.

export type PopularityTrack = {
  title: string;
  artist: string;
  spotifyTrackId: string; // real id, so the backend can look it up later
  plays: number; // raw count, e.g. 2_000_000_000
  playsLabel: string; // display, e.g. "2B plays"
  coverUrl: string; // spotify cover art url (i.scdn.co)
  source: string; // where the number came from
  asOf: string; // date you checked, yyyy-mm-dd
};

export const POPULARITY_ROW: readonly PopularityTrack[] = [
  {
    title: "Blinding Lights",
    artist: "The Weeknd",
    spotifyTrackId: "0VjIjW4GlUZAMYd2vXMi3b",
    plays: 5_620_684_718,
    playsLabel: "5.6B plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a38863bc11d2aa12b54f5aeb36",
    source: "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b",
    asOf: "2026-10-05",
  },
  {
    title: "Cigarettes out the Window",
    artist: "TV Girl",
    spotifyTrackId: "6QeYSvYqYUsfBzsApbjDHO",
    plays: 1_291_169_974,
    playsLabel: "1.3B plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a332f5fec7a879ed6ef28f0dfd",
    source: "https://open.spotify.com/track/6QeYSvYqYUsfBzsApbjDHO",
    asOf: "2026-10-05",
  },
  {
    title: "Pretty Girl",
    artist: "Clairo",
    spotifyTrackId: "3ey2Lbv2YOjgUYKTAIopNS",
    plays: 655_715_051,
    playsLabel: "656M plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a3378a655e1c7ca93207ace890",
    source: "https://open.spotify.com/track/3ey2Lbv2YOjgUYKTAIopNS",
    asOf: "2026-10-05",
  },
  {
    title: "Jonny",
    artist: "Faye Webster",
    spotifyTrackId: "5tuBenbZ1Or9xENTyOKoGC",
    plays: 125_768_702,
    playsLabel: "126M plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a3ac4ebd092fa2cf210e4c8023",
    source: "https://open.spotify.com/track/5tuBenbZ1Or9xENTyOKoGC",
    asOf: "2026-10-05",
  },
  {
    title: "Kill Me",
    artist: "Phoebe Bridgers",
    spotifyTrackId: "2EPxhPbZczxce6wHbuOlQ6",
    plays: 17_030_683,
    playsLabel: "17M plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a325a647ace83ba32770ab5d0f",
    source: "https://open.spotify.com/track/2EPxhPbZczxce6wHbuOlQ6",
    asOf: "2026-10-05",
  },
  {
    title: "Hurt Me",
    artist: "sundots",
    spotifyTrackId: "6jyUSEOeqnbW12Bl5zB2DE",
    plays: 2_569_995,
    playsLabel: "2.6M plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a3bea32f9befef64e18e787ecf",
    source: "https://open.spotify.com/track/6jyUSEOeqnbW12Bl5zB2DE",
    asOf: "2026-10-05",
  },
  {
    title: "No Thank You, I Love You, Goodbye",
    artist: "Lucy Dacus",
    spotifyTrackId: "068okUVy4duZQXGEIQbn4g",
    plays: 801_035,
    playsLabel: "801K plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a36f99cf66717e0819137923fc",
    source: "https://open.spotify.com/track/068okUVy4duZQXGEIQbn4g",
    asOf: "2026-10-05",
  },
  {
    title: "Critical Damage",
    artist: "Sydney Sprague",
    spotifyTrackId: "7fxurSKR96AB4WO9iKfHXK",
    plays: 118_166,
    playsLabel: "118K plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a3ec76de06bc255069b94f3737",
    source: "https://open.spotify.com/track/7fxurSKR96AB4WO9iKfHXK",
    asOf: "2026-10-05",
  },
  {
    title: "The Park",
    artist: "Julia Mendes",
    spotifyTrackId: "30sXr4ngm46jqQqitnje1B",
    plays: 4_663,
    playsLabel: "4.7K plays",
    coverUrl: "https://i.scdn.co/image/ab67616d0000e1a3f9af7e3711f84027aaff1580",
    source: "https://open.spotify.com/track/30sXr4ngm46jqQqitnje1B",
    asOf: "2026-10-05",
  },
];
