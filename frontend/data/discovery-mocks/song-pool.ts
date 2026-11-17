// Deck pool for the mock swipe page. Every artist, song title and album below
// is a real release; most facts are reused from the artist/song data already
// checked against the public Deezer API in taste-graph.ts on 2026-11-16. The
// nine entries marked `verified` reuse the real Spotify track id and cover art
// already confirmed in frontend/data/popularity-row.ts.
//
// `score` and `components` only exist to satisfy the deck API shape; the UI
// never renders them, so the derived values below are deterministic but not
// meaningful data.

import type { DeckItem, SwipeSong } from "@/lib/swipe";

import { songId } from "./song-id";

type PoolSong = {
  slug: string;
  artist: string;
  title: string;
  album: string;
  genre: string;
  relatedArtist: string;
  verified?: { spotifyTrackId: string; albumImageUrl: string };
};

const POOL_SONGS: readonly PoolSong[] = [
  { slug: "clairo", artist: "Clairo", title: "Bags", album: "Bags", genre: "bedroom pop", relatedArtist: "boy pablo" },
  { slug: "clairo", artist: "Clairo", title: "Sofia", album: "Sofia", genre: "bedroom pop", relatedArtist: "girl in red" },
  { slug: "clairo", artist: "Clairo", title: "Pretty Girl", album: "Pretty Girl", genre: "bedroom pop", relatedArtist: "boy pablo", verified: { spotifyTrackId: "3ey2Lbv2YOjgUYKTAIopNS", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a3378a655e1c7ca93207ace890" } },
  { slug: "clairo", artist: "Clairo", title: "Amoeba", album: "Sling", genre: "bedroom pop", relatedArtist: "still woozy" },
  { slug: "tv-girl", artist: "TV Girl", title: "Lovers Rock", album: "French Exit", genre: "bedroom pop", relatedArtist: "cuco" },
  { slug: "tv-girl", artist: "TV Girl", title: "Cigarettes out the Window", album: "Who Really Cares", genre: "bedroom pop", relatedArtist: "Mac DeMarco", verified: { spotifyTrackId: "6QeYSvYqYUsfBzsApbjDHO", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a332f5fec7a879ed6ef28f0dfd" } },
  { slug: "tv-girl", artist: "TV Girl", title: "Not Allowed", album: "Who Really Cares", genre: "bedroom pop", relatedArtist: "Homeshake" },
  { slug: "boy-pablo", artist: "boy pablo", title: "Everytime", album: "Roy Pablo", genre: "bedroom pop", relatedArtist: "Rex Orange County" },
  { slug: "boy-pablo", artist: "boy pablo", title: "Losing You", album: "Soy Pablo", genre: "bedroom pop", relatedArtist: "Dayglow" },
  { slug: "rex-orange-county", artist: "Rex Orange County", title: "Loving Is Easy", album: "Loving is Easy", genre: "bedroom pop", relatedArtist: "Omar Apollo" },
  { slug: "rex-orange-county", artist: "Rex Orange County", title: "Best Friend", album: "Best Friend", genre: "bedroom pop", relatedArtist: "Still Woozy" },
  { slug: "omar-apollo", artist: "Omar Apollo", title: "Ugotme", album: "Stereo", genre: "bedroom pop", relatedArtist: "Steve Lacy" },
  { slug: "omar-apollo", artist: "Omar Apollo", title: "Evergreen (You Didn't Deserve Me At All)", album: "Ivory", genre: "bedroom pop", relatedArtist: "Steve Lacy" },
  { slug: "still-woozy", artist: "Still Woozy", title: "Goodie Bag", album: "Goodie Bag", genre: "bedroom pop", relatedArtist: "Dayglow" },
  { slug: "still-woozy", artist: "Still Woozy", title: "Cooks", album: "Cooks", genre: "bedroom pop", relatedArtist: "Homeshake" },
  { slug: "dayglow", artist: "Dayglow", title: "Can I Call You Tonight?", album: "Fuzzybrain", genre: "indie pop", relatedArtist: "beabadoobee" },
  { slug: "dayglow", artist: "Dayglow", title: "Hot Rod", album: "Fuzzybrain", genre: "indie pop", relatedArtist: "girl in red" },
  { slug: "beabadoobee", artist: "beabadoobee", title: "Coffee", album: "Coffee", genre: "bedroom pop", relatedArtist: "girl in red" },
  { slug: "beabadoobee", artist: "beabadoobee", title: "Care", album: "Fake It Flowers", genre: "bedroom pop", relatedArtist: "Snail Mail" },
  { slug: "girl-in-red", artist: "girl in red", title: "we fell in love in october", album: "we fell in love in october / forget her", genre: "bedroom pop", relatedArtist: "Soccer Mommy" },
  { slug: "girl-in-red", artist: "girl in red", title: "i wanna be your girlfriend", album: "chapter 1", genre: "bedroom pop", relatedArtist: "Sydney Sprague" },
  { slug: "mac-demarco", artist: "Mac DeMarco", title: "Chamber of Reflection", album: "Salad Days", genre: "lo-fi", relatedArtist: "Homeshake" },
  { slug: "mac-demarco", artist: "Mac DeMarco", title: "My Kind of Woman", album: "2", genre: "lo-fi", relatedArtist: "Unknown Mortal Orchestra" },
  { slug: "mac-demarco", artist: "Mac DeMarco", title: "Ode to Viceroy", album: "2", genre: "lo-fi", relatedArtist: "King Krule" },
  { slug: "homeshake", artist: "Homeshake", title: "Khmlwugh", album: "Fresh Air", genre: "lo-fi", relatedArtist: "Steve Lacy" },
  { slug: "homeshake", artist: "Homeshake", title: "Call Me Up", album: "Fresh Air", genre: "lo-fi", relatedArtist: "Yellow Days" },
  { slug: "steve-lacy", artist: "Steve Lacy", title: "Dark Red", album: "Steve Lacy's Demo", genre: "lo-fi", relatedArtist: "sundots" },
  { slug: "sundots", artist: "sundots", title: "Hurt Me", album: "Honeyspot", genre: "lo-fi", relatedArtist: "Clairo", verified: { spotifyTrackId: "6jyUSEOeqnbW12Bl5zB2DE", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a3bea32f9befef64e18e787ecf" } },
  { slug: "yellow-days", artist: "Yellow Days", title: "Your Hand Holding Mine", album: "Harmless Melodies", genre: "lo-fi", relatedArtist: "King Krule" },
  { slug: "phoebe-bridgers", artist: "Phoebe Bridgers", title: "Motion Sickness", album: "Stranger in the Alps", genre: "indie folk", relatedArtist: "Lucy Dacus" },
  { slug: "phoebe-bridgers", artist: "Phoebe Bridgers", title: "Garden Song", album: "Punisher", genre: "indie folk", relatedArtist: "Faye Webster" },
  { slug: "phoebe-bridgers", artist: "Phoebe Bridgers", title: "Kill Me", album: "Lost Weekend", genre: "indie folk", relatedArtist: "Lucy Dacus", verified: { spotifyTrackId: "2EPxhPbZczxce6wHbuOlQ6", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a325a647ace83ba32770ab5d0f" } },
  { slug: "phoebe-bridgers", artist: "Phoebe Bridgers", title: "Scott Street", album: "Stranger in the Alps", genre: "indie folk", relatedArtist: "Waxahatchee" },
  { slug: "lucy-dacus", artist: "Lucy Dacus", title: "Night Shift", album: "Historian", genre: "indie folk", relatedArtist: "Phoebe Bridgers" },
  { slug: "lucy-dacus", artist: "Lucy Dacus", title: "Hot & Heavy", album: "Home Video", genre: "indie folk", relatedArtist: "Faye Webster" },
  { slug: "lucy-dacus", artist: "Lucy Dacus", title: "No Thank You, I Love You, Goodbye", album: "No Thank You, I Love You, Goodbye", genre: "indie folk", relatedArtist: "Phoebe Bridgers", verified: { spotifyTrackId: "068okUVy4duZQXGEIQbn4g", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a36f99cf66717e0819137923fc" } },
  { slug: "faye-webster", artist: "Faye Webster", title: "Kingston", album: "Atlanta Millionaires Club", genre: "indie folk", relatedArtist: "Lucy Dacus" },
  { slug: "faye-webster", artist: "Faye Webster", title: "Right Side of My Neck", album: "Atlanta Millionaires Club", genre: "indie folk", relatedArtist: "Andy Shauf" },
  { slug: "faye-webster", artist: "Faye Webster", title: "Jonny", album: "Atlanta Millionaires Club", genre: "indie folk", relatedArtist: "MJ Lenderman", verified: { spotifyTrackId: "5tuBenbZ1Or9xENTyOKoGC", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a3ac4ebd092fa2cf210e4c8023" } },
  { slug: "big-thief", artist: "Big Thief", title: "Not", album: "Two Hands", genre: "indie folk", relatedArtist: "Sharon Van Etten" },
  { slug: "big-thief", artist: "Big Thief", title: "Simulation Swarm", album: "Dragon New Warm Mountain I Believe In You", genre: "indie folk", relatedArtist: "Hovvdy" },
  { slug: "big-thief", artist: "Big Thief", title: "Masterpiece", album: "Masterpiece", genre: "indie folk", relatedArtist: "MJ Lenderman" },
  { slug: "waxahatchee", artist: "Waxahatchee", title: "Can't Do Much", album: "Saint Cloud", genre: "indie folk", relatedArtist: "Angel Olsen" },
  { slug: "waxahatchee", artist: "Waxahatchee", title: "Right Back to It", album: "Tigers Blood", genre: "indie folk", relatedArtist: "MJ Lenderman" },
  { slug: "angel-olsen", artist: "Angel Olsen", title: "Shut Up Kiss Me", album: "MY WOMAN", genre: "singer-songwriter", relatedArtist: "Sharon Van Etten" },
  { slug: "sharon-van-etten", artist: "Sharon Van Etten", title: "Seventeen", album: "Remind Me Tomorrow", genre: "singer-songwriter", relatedArtist: "Mitski" },
  { slug: "bon-iver", artist: "Bon Iver", title: "Skinny Love", album: "For Emma, Forever Ago", genre: "indie folk", relatedArtist: "Fleet Foxes" },
  { slug: "fleet-foxes", artist: "Fleet Foxes", title: "White Winter Hymnal", album: "Fleet Foxes", genre: "indie folk", relatedArtist: "Andy Shauf" },
  { slug: "nick-drake", artist: "Nick Drake", title: "Pink Moon", album: "Pink Moon", genre: "singer-songwriter", relatedArtist: "Haley Heynderickx" },
  { slug: "haley-heynderickx", artist: "Haley Heynderickx", title: "The Bug Collector", album: "I Need to Start a Garden", genre: "indie folk", relatedArtist: "Andy Shauf" },
  { slug: "andy-shauf", artist: "Andy Shauf", title: "The Magician", album: "The Party", genre: "indie folk", relatedArtist: "MJ Lenderman" },
  { slug: "hovvdy", artist: "Hovvdy", title: "Runner", album: "Runner", genre: "slowcore", relatedArtist: "Duster" },
  { slug: "mj-lenderman", artist: "MJ Lenderman", title: "She's Leaving You", album: "Manning Fireworks", genre: "indie rock", relatedArtist: "Hop Along" },
  { slug: "tame-impala", artist: "Tame Impala", title: "Let It Happen", album: "Currents", genre: "psych rock", relatedArtist: "Unknown Mortal Orchestra" },
  { slug: "unknown-mortal-orchestra", artist: "Unknown Mortal Orchestra", title: "Hunnybee", album: "Sex & Food", genre: "psych rock", relatedArtist: "Mild High Club" },
  { slug: "toro-y-moi", artist: "Toro y Moi", title: "Still Sound", album: "Underneath The Pine", genre: "chillwave", relatedArtist: "Washed Out" },
  { slug: "washed-out", artist: "Washed Out", title: "Feel It All Around", album: "Life of Leisure", genre: "chillwave", relatedArtist: "Neon Indian" },
  { slug: "khruangbin", artist: "Khruangbin", title: "White Gloves", album: "White Gloves", genre: "psych funk", relatedArtist: "Toro y Moi" },
  { slug: "mild-high-club", artist: "Mild High Club", title: "Homage", album: "Skiptracing", genre: "psych rock", relatedArtist: "Crumb" },
  { slug: "crumb", artist: "Crumb", title: "Locket", album: "Locket", genre: "dream pop", relatedArtist: "Men I Trust" },
  { slug: "king-krule", artist: "King Krule", title: "Easy Easy", album: "6 Feet Beneath The Moon", genre: "lo-fi", relatedArtist: "Alex G" },
  { slug: "alex-g", artist: "Alex G", title: "Gretel", album: "House of Sugar", genre: "lo-fi", relatedArtist: "Duster" },
  { slug: "beach-house", artist: "Beach House", title: "Space Song", album: "Depression Cherry", genre: "dream pop", relatedArtist: "Slowdive" },
  { slug: "slowdive", artist: "Slowdive", title: "Alison", album: "Souvlaki", genre: "shoegaze", relatedArtist: "Cocteau Twins" },
  { slug: "my-bloody-valentine", artist: "My Bloody Valentine", title: "Only Shallow", album: "loveless", genre: "shoegaze", relatedArtist: "Slowdive" },
  { slug: "cocteau-twins", artist: "Cocteau Twins", title: "Cherry-Coloured Funk", album: "Heaven or Las Vegas", genre: "dream pop", relatedArtist: "Wild Nothing" },
  { slug: "duster", artist: "Duster", title: "Inside Out", album: "Stratosphere", genre: "slowcore", relatedArtist: "Cigarettes After Sex" },
  { slug: "diiv", artist: "DIIV", title: "Doused", album: "Oshin", genre: "shoegaze", relatedArtist: "Beach Fossils" },
  { slug: "beach-fossils", artist: "Beach Fossils", title: "Sleep Apnea", album: "Clash the Truth", genre: "dream pop", relatedArtist: "Wild Nothing" },
  { slug: "wild-nothing", artist: "Wild Nothing", title: "Chinatown", album: "Gemini", genre: "dream pop", relatedArtist: "Hatchie" },
  { slug: "cigarettes-after-sex", artist: "Cigarettes After Sex", title: "Apocalypse", album: "Cigarettes After Sex", genre: "dream pop", relatedArtist: "Men I Trust" },
  { slug: "hatchie", artist: "Hatchie", title: "Sure", album: "Sugar & Spice", genre: "dream pop", relatedArtist: "Snail Mail" },
  { slug: "men-i-trust", artist: "Men I Trust", title: "Show Me How", album: "Show Me How", genre: "dream pop", relatedArtist: "Japanese Breakfast" },
  { slug: "snail-mail", artist: "Snail Mail", title: "Pristine", album: "Lush", genre: "indie rock", relatedArtist: "Soccer Mommy" },
  { slug: "soccer-mommy", artist: "Soccer Mommy", title: "Circle the Drain", album: "circle the drain", genre: "indie rock", relatedArtist: "Mitski" },
  { slug: "japanese-breakfast", artist: "Japanese Breakfast", title: "Be Sweet", album: "Jubilee", genre: "indie rock", relatedArtist: "Mitski" },
  { slug: "mitski", artist: "Mitski", title: "Nobody", album: "Be the Cowboy", genre: "indie rock", relatedArtist: "Hop Along" },
  { slug: "hop-along", artist: "Hop Along", title: "Waitress", album: "Painted Shut", genre: "indie rock", relatedArtist: "Sydney Sprague" },
  { slug: "sydney-sprague", artist: "Sydney Sprague", title: "Critical Damage", album: "Peak Experience", genre: "indie rock", relatedArtist: "Mitski", verified: { spotifyTrackId: "7fxurSKR96AB4WO9iKfHXK", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a3ec76de06bc255069b94f3737" } },
  { slug: "wednesday", artist: "Wednesday", title: "Chosen to Deserve", album: "Rat Saw God", genre: "indie rock", relatedArtist: "Hop Along" },
  { slug: "julia-mendes", artist: "Julia Mendes", title: "The Park", album: "The Park", genre: "indie pop", relatedArtist: "Clairo", verified: { spotifyTrackId: "30sXr4ngm46jqQqitnje1B", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a3f9af7e3711f84027aaff1580" } },
  { slug: "the-weeknd", artist: "The Weeknd", title: "Blinding Lights", album: "After Hours", genre: "synth pop", relatedArtist: "Toro y Moi", verified: { spotifyTrackId: "0VjIjW4GlUZAMYd2vXMi3b", albumImageUrl: "https://i.scdn.co/image/ab67616d0000e1a38863bc11d2aa12b54f5aeb36" } },
];

function hashToUnit(seed: string): number {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return (hash % 1000) / 1000;
}

function buildDeckItem(pool: PoolSong): DeckItem {
  const id = songId(pool.slug, pool.title);
  const song: SwipeSong = {
    id,
    title: pool.title,
    artist: pool.artist,
    album: pool.album,
    album_image_url: pool.verified?.albumImageUrl ?? null,
    preview_url: null,
    spotify_url: pool.verified
      ? `https://open.spotify.com/track/${pool.verified.spotifyTrackId}`
      : null,
  };

  return {
    song,
    reason: {
      text: `${pool.relatedArtist} and ${pool.artist} share a ${pool.genre} sound.`,
      path: [pool.relatedArtist, pool.artist],
    },
    score: hashToUnit(id),
    components: {
      graph: hashToUnit(`${id}:graph`),
      similarity: hashToUnit(`${id}:similarity`),
      discovery: hashToUnit(`${id}:discovery`),
    },
  };
}

export const DECK_POOL: readonly DeckItem[] = POOL_SONGS.map(buildDeckItem);

export function songsForArtist(slug: string): readonly DeckItem[] {
  return DECK_POOL.filter((item, index) => POOL_SONGS[index]?.slug === slug);
}
