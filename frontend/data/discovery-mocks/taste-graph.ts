// Sample taste graph for the mock discovery pages. Every artist, song title and
// album below is a real release; each artist/title/album triple was checked
// against the public Deezer API on 2026-11-16. Nothing here is generated.
//
// Node weights, tag counts and edge weights are derived from this data at the
// bottom of the file, so they cannot drift out of sync with it.
//
// Artists in CATALOG are the user's own; artists in FRONTIER are deliberately
// absent from the `artists` record, which is what marks them as new to the user.

import type {
  TasteArtistDetail,
  TasteEdge,
  TasteEdgeKind,
  TasteGraphResponse,
  TasteNode,
} from "@/lib/taste";

import { songId } from "./song-id";

type TagSlug =
  | "bedroom-pop"
  | "indie-pop"
  | "lo-fi"
  | "indie-folk"
  | "singer-songwriter"
  | "slowcore"
  | "psych-rock"
  | "chillwave"
  | "psych-funk"
  | "dream-pop"
  | "shoegaze"
  | "indie-rock";

type CatalogSong = {
  title: string;
  album: string;
};

type CatalogArtist = {
  slug: string;
  name: string;
  tags: readonly TagSlug[];
  similar: readonly string[];
  songs: readonly CatalogSong[];
};

type FrontierArtist = {
  slug: string;
  name: string;
  similar: readonly string[];
};

const TAG_LABELS: Record<TagSlug, string> = {
  "bedroom-pop": "Bedroom pop",
  "indie-pop": "Indie pop",
  "lo-fi": "Lo-fi",
  "indie-folk": "Indie folk",
  "singer-songwriter": "Singer-songwriter",
  slowcore: "Slowcore",
  "psych-rock": "Psych rock",
  chillwave: "Chillwave",
  "psych-funk": "Psych funk",
  "dream-pop": "Dream pop",
  shoegaze: "Shoegaze",
  "indie-rock": "Indie rock",
};

const TAG_SLUGS = Object.keys(TAG_LABELS) as TagSlug[];

const CATALOG: readonly CatalogArtist[] = [
  {
    slug: "clairo",
    name: "Clairo",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["boy-pablo", "girl-in-red", "beabadoobee", "soccer-mommy"],
    songs: [
      { title: "Bags", album: "Bags" },
      { title: "Sofia", album: "Sofia" },
      { title: "Pretty Girl", album: "Pretty Girl" },
      { title: "Amoeba", album: "Sling" },
    ],
  },
  {
    slug: "tv-girl",
    name: "TV Girl",
    tags: ["bedroom-pop", "lo-fi"],
    similar: ["cuco", "yellow-days", "homeshake", "mac-demarco"],
    songs: [
      { title: "Lovers Rock", album: "French Exit" },
      { title: "Cigarettes out the Window", album: "Who Really Cares" },
      { title: "Not Allowed", album: "Who Really Cares" },
    ],
  },
  {
    slug: "boy-pablo",
    name: "boy pablo",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["rex-orange-county", "still-woozy", "dayglow"],
    songs: [
      { title: "Everytime", album: "Roy Pablo" },
      { title: "Losing You", album: "Soy Pablo" },
    ],
  },
  {
    slug: "rex-orange-county",
    name: "Rex Orange County",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["omar-apollo", "still-woozy", "steve-lacy"],
    songs: [
      { title: "Loving Is Easy", album: "Loving is Easy" },
      { title: "Best Friend", album: "Best Friend" },
    ],
  },
  {
    slug: "omar-apollo",
    name: "Omar Apollo",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["steve-lacy", "still-woozy"],
    songs: [
      { title: "Ugotme", album: "Stereo" },
      { title: "Evergreen (You Didn't Deserve Me At All)", album: "Ivory" },
    ],
  },
  {
    slug: "cuco",
    name: "Cuco",
    tags: ["bedroom-pop", "lo-fi"],
    similar: ["yellow-days", "sundots", "homeshake"],
    songs: [{ title: "Lo Que Siento", album: "Lo Que Siento" }],
  },
  {
    slug: "still-woozy",
    name: "Still Woozy",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["dayglow", "homeshake"],
    songs: [
      { title: "Goodie Bag", album: "Goodie Bag" },
      { title: "Cooks", album: "Cooks" },
    ],
  },
  {
    slug: "dayglow",
    name: "Dayglow",
    tags: ["indie-pop"],
    similar: ["beabadoobee", "girl-in-red"],
    songs: [
      { title: "Can I Call You Tonight?", album: "Fuzzybrain" },
      { title: "Hot Rod", album: "Fuzzybrain" },
    ],
  },
  {
    slug: "beabadoobee",
    name: "beabadoobee",
    tags: ["bedroom-pop", "indie-rock"],
    similar: ["girl-in-red", "snail-mail", "soccer-mommy"],
    songs: [
      { title: "Coffee", album: "Coffee" },
      { title: "Care", album: "Fake It Flowers" },
    ],
  },
  {
    slug: "girl-in-red",
    name: "girl in red",
    tags: ["bedroom-pop", "indie-pop"],
    similar: ["soccer-mommy", "sydney-sprague"],
    songs: [
      {
        title: "we fell in love in october",
        album: "we fell in love in october / forget her",
      },
      { title: "i wanna be your girlfriend", album: "chapter 1" },
    ],
  },
  {
    slug: "mac-demarco",
    name: "Mac DeMarco",
    tags: ["lo-fi", "indie-pop"],
    similar: [
      "homeshake",
      "king-krule",
      "alex-g",
      "unknown-mortal-orchestra",
    ],
    songs: [
      { title: "Chamber of Reflection", album: "Salad Days" },
      { title: "My Kind of Woman", album: "2" },
      { title: "Ode to Viceroy", album: "2" },
    ],
  },
  {
    slug: "homeshake",
    name: "Homeshake",
    tags: ["lo-fi", "bedroom-pop"],
    similar: ["yellow-days", "steve-lacy"],
    songs: [
      { title: "Khmlwugh", album: "Fresh Air" },
      { title: "Call Me Up", album: "Fresh Air" },
    ],
  },
  {
    slug: "steve-lacy",
    name: "Steve Lacy",
    tags: ["bedroom-pop", "lo-fi"],
    similar: ["toro-y-moi", "sundots"],
    songs: [{ title: "Dark Red", album: "Steve Lacy's Demo" }],
  },
  {
    slug: "sundots",
    name: "sundots",
    tags: ["bedroom-pop", "lo-fi"],
    similar: ["yellow-days", "clairo"],
    songs: [{ title: "Hurt Me", album: "Honeyspot" }],
  },
  {
    slug: "yellow-days",
    name: "Yellow Days",
    tags: ["bedroom-pop", "lo-fi"],
    similar: ["king-krule"],
    songs: [{ title: "Your Hand Holding Mine", album: "Harmless Melodies" }],
  },
  {
    slug: "phoebe-bridgers",
    name: "Phoebe Bridgers",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["lucy-dacus", "faye-webster", "waxahatchee", "elliott-smith"],
    songs: [
      { title: "Motion Sickness", album: "Stranger in the Alps" },
      { title: "Garden Song", album: "Punisher" },
      { title: "Kill Me", album: "Lost Weekend" },
      { title: "Scott Street", album: "Stranger in the Alps" },
    ],
  },
  {
    slug: "lucy-dacus",
    name: "Lucy Dacus",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["faye-webster", "waxahatchee", "hop-along"],
    songs: [
      { title: "Night Shift", album: "Historian" },
      { title: "Hot & Heavy", album: "Home Video" },
      {
        title: "No Thank You, I Love You, Goodbye",
        album: "No Thank You, I Love You, Goodbye",
      },
    ],
  },
  {
    slug: "faye-webster",
    name: "Faye Webster",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["waxahatchee", "andy-shauf", "mj-lenderman"],
    songs: [
      { title: "Kingston", album: "Atlanta Millionaires Club" },
      { title: "Right Side of My Neck", album: "Atlanta Millionaires Club" },
      { title: "Jonny", album: "Atlanta Millionaires Club" },
    ],
  },
  {
    slug: "adrianne-lenker",
    name: "Adrianne Lenker",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["big-thief", "nick-drake", "haley-heynderickx"],
    songs: [
      { title: "anything", album: "songs" },
      { title: "half return", album: "songs" },
    ],
  },
  {
    slug: "big-thief",
    name: "Big Thief",
    tags: ["indie-folk", "indie-rock"],
    similar: ["mj-lenderman", "hovvdy", "sharon-van-etten"],
    songs: [
      { title: "Not", album: "Two Hands" },
      {
        title: "Simulation Swarm",
        album: "Dragon New Warm Mountain I Believe In You",
      },
      { title: "Masterpiece", album: "Masterpiece" },
    ],
  },
  {
    slug: "waxahatchee",
    name: "Waxahatchee",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["mj-lenderman", "angel-olsen"],
    songs: [
      { title: "Can't Do Much", album: "Saint Cloud" },
      { title: "Fire", album: "Saint Cloud" },
      { title: "Right Back to It", album: "Tigers Blood" },
    ],
  },
  {
    slug: "angel-olsen",
    name: "Angel Olsen",
    tags: ["singer-songwriter", "indie-folk"],
    similar: ["sharon-van-etten", "mitski"],
    songs: [
      { title: "Shut Up Kiss Me", album: "MY WOMAN" },
      { title: "Lark", album: "All Mirrors" },
    ],
  },
  {
    slug: "sharon-van-etten",
    name: "Sharon Van Etten",
    tags: ["singer-songwriter", "indie-rock"],
    similar: ["mitski", "hop-along"],
    songs: [
      { title: "Seventeen", album: "Remind Me Tomorrow" },
      { title: "Comeback Kid", album: "Remind Me Tomorrow" },
    ],
  },
  {
    slug: "sufjan-stevens",
    name: "Sufjan Stevens",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["bon-iver", "fleet-foxes", "nick-drake"],
    songs: [{ title: "Chicago", album: "Illinois" }],
  },
  {
    slug: "bon-iver",
    name: "Bon Iver",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["fleet-foxes", "hovvdy"],
    songs: [
      { title: "Skinny Love", album: "For Emma, Forever Ago" },
      { title: "Holocene", album: "Bon Iver, Bon Iver" },
    ],
  },
  {
    slug: "fleet-foxes",
    name: "Fleet Foxes",
    tags: ["indie-folk"],
    similar: ["andy-shauf"],
    songs: [
      { title: "White Winter Hymnal", album: "Fleet Foxes" },
      { title: "Mykonos", album: "Sun Giant EP" },
    ],
  },
  {
    slug: "elliott-smith",
    name: "Elliott Smith",
    tags: ["singer-songwriter", "lo-fi"],
    similar: ["nick-drake", "alex-g", "duster"],
    songs: [
      { title: "Between the Bars", album: "Either/Or" },
      { title: "Say Yes", album: "Either/Or" },
    ],
  },
  {
    slug: "nick-drake",
    name: "Nick Drake",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["haley-heynderickx"],
    songs: [
      { title: "Pink Moon", album: "Pink Moon" },
      { title: "River Man", album: "Five Leaves Left" },
    ],
  },
  {
    slug: "haley-heynderickx",
    name: "Haley Heynderickx",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["andy-shauf", "hovvdy"],
    songs: [
      { title: "Oom Sha La La", album: "I Need to Start a Garden" },
      { title: "The Bug Collector", album: "I Need to Start a Garden" },
    ],
  },
  {
    slug: "andy-shauf",
    name: "Andy Shauf",
    tags: ["indie-folk", "singer-songwriter"],
    similar: ["mj-lenderman"],
    songs: [
      { title: "The Magician", album: "The Party" },
      { title: "Try Again", album: "The Neon Skyline" },
    ],
  },
  {
    slug: "hovvdy",
    name: "Hovvdy",
    tags: ["indie-folk", "slowcore"],
    similar: ["duster", "cigarettes-after-sex"],
    songs: [
      { title: "Runner", album: "Runner" },
      { title: "True Love", album: "True Love" },
    ],
  },
  {
    slug: "mj-lenderman",
    name: "MJ Lenderman",
    tags: ["indie-folk", "indie-rock"],
    similar: ["hop-along", "wednesday"],
    songs: [
      { title: "She's Leaving You", album: "Manning Fireworks" },
      { title: "Hangover Game", album: "Boat Songs" },
    ],
  },
  {
    slug: "tame-impala",
    name: "Tame Impala",
    tags: ["psych-rock"],
    similar: ["unknown-mortal-orchestra", "toro-y-moi", "crumb"],
    songs: [
      { title: "Let It Happen", album: "Currents" },
      { title: "The Less I Know the Better", album: "Currents" },
    ],
  },
  {
    slug: "unknown-mortal-orchestra",
    name: "Unknown Mortal Orchestra",
    tags: ["psych-rock", "lo-fi"],
    similar: ["mild-high-club", "crumb", "king-krule"],
    songs: [
      { title: "Hunnybee", album: "Sex & Food" },
      { title: "Multi-Love", album: "Multi-Love" },
      { title: "So Good at Being in Trouble", album: "II" },
    ],
  },
  {
    slug: "toro-y-moi",
    name: "Toro y Moi",
    tags: ["chillwave", "psych-funk"],
    similar: ["washed-out", "neon-indian", "khruangbin"],
    songs: [
      { title: "Still Sound", album: "Underneath The Pine" },
      { title: "So Many Details", album: "Anything in Return" },
    ],
  },
  {
    slug: "washed-out",
    name: "Washed Out",
    tags: ["chillwave", "dream-pop"],
    similar: ["neon-indian", "beach-house"],
    songs: [
      { title: "Feel It All Around", album: "Life of Leisure" },
      { title: "Amor Fati", album: "Within and Without" },
    ],
  },
  {
    slug: "neon-indian",
    name: "Neon Indian",
    tags: ["chillwave"],
    similar: ["mild-high-club"],
    songs: [{ title: "Polish Girl", album: "Era Extra\u00f1a" }],
  },
  {
    slug: "khruangbin",
    name: "Khruangbin",
    tags: ["psych-funk"],
    similar: ["mild-high-club", "crumb"],
    songs: [
      { title: "White Gloves", album: "White Gloves" },
      { title: "August 10", album: "Con Todo El Mundo" },
      { title: "Time (You and I)", album: "Time (You and I)" },
    ],
  },
  {
    slug: "mild-high-club",
    name: "Mild High Club",
    tags: ["psych-rock", "lo-fi"],
    similar: ["crumb", "alex-g"],
    songs: [
      { title: "Homage", album: "Skiptracing" },
      { title: "Skiptracing", album: "Skiptracing" },
    ],
  },
  {
    slug: "crumb",
    name: "Crumb",
    tags: ["psych-rock", "dream-pop"],
    similar: ["men-i-trust", "japanese-breakfast"],
    songs: [
      { title: "Locket", album: "Locket" },
      { title: "Part III", album: "Jinx" },
    ],
  },
  {
    slug: "king-krule",
    name: "King Krule",
    tags: ["lo-fi", "psych-rock"],
    similar: ["alex-g", "duster"],
    songs: [
      { title: "Easy Easy", album: "6 Feet Beneath The Moon" },
      { title: "Baby Blue", album: "6 Feet Beneath The Moon" },
    ],
  },
  {
    slug: "alex-g",
    name: "Alex G",
    tags: ["lo-fi", "indie-rock"],
    similar: ["duster", "soccer-mommy"],
    songs: [
      { title: "Gretel", album: "House of Sugar" },
      { title: "Mary", album: "Trick" },
    ],
  },
  {
    slug: "beach-house",
    name: "Beach House",
    tags: ["dream-pop", "shoegaze"],
    similar: ["slowdive", "cocteau-twins", "wild-nothing"],
    songs: [
      { title: "Space Song", album: "Depression Cherry" },
      { title: "Myth", album: "Bloom" },
      { title: "Zebra", album: "Teen Dream" },
    ],
  },
  {
    slug: "slowdive",
    name: "Slowdive",
    tags: ["shoegaze", "dream-pop"],
    similar: ["my-bloody-valentine", "cocteau-twins", "diiv"],
    songs: [
      { title: "Alison", album: "Souvlaki" },
      { title: "Sugar for the Pill", album: "Slowdive" },
    ],
  },
  {
    slug: "my-bloody-valentine",
    name: "My Bloody Valentine",
    tags: ["shoegaze"],
    similar: ["diiv", "wednesday"],
    songs: [
      { title: "Only Shallow", album: "loveless" },
      { title: "Sometimes", album: "loveless" },
    ],
  },
  {
    slug: "cocteau-twins",
    name: "Cocteau Twins",
    tags: ["dream-pop", "shoegaze"],
    similar: ["wild-nothing", "hatchie"],
    songs: [
      { title: "Cherry-Coloured Funk", album: "Heaven or Las Vegas" },
      { title: "Heaven or Las Vegas", album: "Heaven or Las Vegas" },
    ],
  },
  {
    slug: "duster",
    name: "Duster",
    tags: ["slowcore", "lo-fi"],
    similar: ["cigarettes-after-sex", "beach-fossils"],
    songs: [
      { title: "Inside Out", album: "Stratosphere" },
      { title: "Stratosphere", album: "Stratosphere" },
    ],
  },
  {
    slug: "diiv",
    name: "DIIV",
    tags: ["shoegaze", "dream-pop"],
    similar: ["beach-fossils", "wild-nothing"],
    songs: [
      { title: "Doused", album: "Oshin" },
      { title: "Under the Sun", album: "Is the Is Are" },
    ],
  },
  {
    slug: "beach-fossils",
    name: "Beach Fossils",
    tags: ["dream-pop", "indie-rock"],
    similar: ["wild-nothing", "men-i-trust"],
    songs: [
      { title: "Sleep Apnea", album: "Clash the Truth" },
      { title: "Down the Line", album: "Somersault" },
    ],
  },
  {
    slug: "wild-nothing",
    name: "Wild Nothing",
    tags: ["dream-pop", "shoegaze"],
    similar: ["hatchie"],
    songs: [{ title: "Chinatown", album: "Gemini" }],
  },
  {
    slug: "cigarettes-after-sex",
    name: "Cigarettes After Sex",
    tags: ["dream-pop", "slowcore"],
    similar: ["men-i-trust", "hatchie"],
    songs: [
      { title: "Apocalypse", album: "Cigarettes After Sex" },
      { title: "Sunsetz", album: "Cigarettes After Sex" },
    ],
  },
  {
    slug: "hatchie",
    name: "Hatchie",
    tags: ["dream-pop", "shoegaze"],
    similar: ["snail-mail", "japanese-breakfast"],
    songs: [{ title: "Sure", album: "Sugar & Spice" }],
  },
  {
    slug: "men-i-trust",
    name: "Men I Trust",
    tags: ["dream-pop", "indie-pop"],
    similar: ["japanese-breakfast"],
    songs: [
      { title: "Show Me How", album: "Show Me How" },
      { title: "Tailwhip", album: "Tailwhip" },
      { title: "Numb", album: "Numb" },
    ],
  },
  {
    slug: "snail-mail",
    name: "Snail Mail",
    tags: ["indie-rock", "indie-pop"],
    similar: ["soccer-mommy", "japanese-breakfast", "wednesday"],
    songs: [
      { title: "Pristine", album: "Lush" },
      { title: "Heat Wave", album: "Lush" },
    ],
  },
  {
    slug: "soccer-mommy",
    name: "Soccer Mommy",
    tags: ["indie-rock", "bedroom-pop"],
    similar: ["mitski", "sydney-sprague"],
    songs: [
      { title: "Circle the Drain", album: "circle the drain" },
      { title: "Your Dog", album: "Clean" },
    ],
  },
  {
    slug: "japanese-breakfast",
    name: "Japanese Breakfast",
    tags: ["indie-rock", "dream-pop"],
    similar: ["mitski", "wednesday"],
    songs: [
      { title: "Be Sweet", album: "Jubilee" },
      { title: "Road Head", album: "Soft Sounds from Another Planet" },
    ],
  },
  {
    slug: "mitski",
    name: "Mitski",
    tags: ["indie-rock", "singer-songwriter"],
    similar: ["hop-along", "sydney-sprague"],
    songs: [
      { title: "Nobody", album: "Be the Cowboy" },
      { title: "Washing Machine Heart", album: "Be the Cowboy" },
      { title: "Your Best American Girl", album: "Puberty 2" },
    ],
  },
  {
    slug: "hop-along",
    name: "Hop Along",
    tags: ["indie-rock", "indie-folk"],
    similar: ["sydney-sprague", "wednesday"],
    songs: [
      { title: "Waitress", album: "Painted Shut" },
      { title: "How Simple", album: "Bark Your Head Off, Dog" },
    ],
  },
  {
    slug: "sydney-sprague",
    name: "Sydney Sprague",
    tags: ["indie-rock", "indie-pop"],
    similar: ["wednesday"],
    songs: [
      {
        title: "i refuse to die",
        album: "maybe i will see you at the end of the world",
      },
      { title: "Critical Damage", album: "Peak Experience" },
    ],
  },
  {
    slug: "wednesday",
    name: "Wednesday",
    tags: ["indie-rock", "shoegaze"],
    similar: [],
    songs: [{ title: "Chosen to Deserve", album: "Rat Saw God" }],
  },
];

const FRONTIER: readonly FrontierArtist[] = [
  {
    slug: "momma",
    name: "Momma",
    similar: ["snail-mail", "soccer-mommy", "wednesday"],
  },
  {
    slug: "horsegirl",
    name: "Horsegirl",
    similar: ["wednesday", "snail-mail", "my-bloody-valentine"],
  },
  {
    slug: "mild-orange",
    name: "Mild Orange",
    similar: ["men-i-trust", "beach-fossils"],
  },
  {
    slug: "hers",
    name: "Her's",
    similar: ["mac-demarco", "men-i-trust", "beach-fossils"],
  },
  {
    slug: "inner-wave",
    name: "Inner Wave",
    similar: ["toro-y-moi", "khruangbin", "mild-high-club"],
  },
  {
    slug: "melodys-echo-chamber",
    name: "Melody's Echo Chamber",
    similar: ["tame-impala", "crumb"],
  },
  {
    slug: "connan-mockasin",
    name: "Connan Mockasin",
    similar: ["unknown-mortal-orchestra", "mild-high-club"],
  },
  {
    slug: "julie-byrne",
    name: "Julie Byrne",
    similar: ["adrianne-lenker", "nick-drake", "haley-heynderickx"],
  },
  {
    slug: "florist",
    name: "Florist",
    similar: ["hovvdy", "adrianne-lenker"],
  },
  {
    slug: "bedouine",
    name: "Bedouine",
    similar: ["nick-drake", "andy-shauf", "angel-olsen"],
  },
];

const CATALOG_BY_SLUG = new Map(CATALOG.map((artist) => [artist.slug, artist]));

function nodeIdForSlug(slug: string): string {
  return CATALOG_BY_SLUG.has(slug) ? `artist:${slug}` : `frontier:${slug}`;
}

function sharedTagCount(a: string, b: string): number {
  const left = CATALOG_BY_SLUG.get(a);
  const right = CATALOG_BY_SLUG.get(b);
  if (!left || !right) {
    return 0;
  }
  return left.tags.filter((tag) => right.tags.includes(tag)).length;
}

function buildGraph(): TasteGraphResponse {
  const nodes: TasteNode[] = [
    ...TAG_SLUGS.map((slug) => ({
      id: `tag:${slug}`,
      kind: "tag" as const,
      label: TAG_LABELS[slug],
      weight: CATALOG.filter((artist) => artist.tags.includes(slug)).length,
    })),
    ...CATALOG.map((artist) => ({
      id: `artist:${artist.slug}`,
      kind: "artist" as const,
      label: artist.name,
      weight: artist.songs.length,
    })),
    ...FRONTIER.map((artist) => ({
      id: `frontier:${artist.slug}`,
      kind: "frontier" as const,
      label: artist.name,
      weight: artist.similar.filter((slug) => CATALOG_BY_SLUG.has(slug)).length,
    })),
  ];

  const edges: TasteEdge[] = [];
  const seen = new Set<string>();

  const addEdge = (
    src: string,
    dst: string,
    kind: TasteEdgeKind,
    weight: number,
  ) => {
    const key = [kind, src, dst].sort().join("|");
    if (!seen.has(key)) {
      seen.add(key);
      edges.push({ src, dst, kind, weight });
    }
  };

  for (const artist of CATALOG) {
    for (const tag of artist.tags) {
      addEdge(
        `artist:${artist.slug}`,
        `tag:${tag}`,
        "tagged",
        artist.songs.length,
      );
    }
  }

  for (const artist of [...CATALOG, ...FRONTIER]) {
    for (const other of artist.similar) {
      addEdge(
        nodeIdForSlug(artist.slug),
        nodeIdForSlug(other),
        "similar",
        Math.max(1, sharedTagCount(artist.slug, other)),
      );
    }
  }

  const artists: Record<string, TasteArtistDetail> = {};
  for (const artist of CATALOG) {
    artists[`artist:${artist.slug}`] = {
      songs: artist.songs.map((song) => ({
        id: songId(artist.slug, song.title),
        title: song.title,
        album: song.album,
      })),
    };
  }

  return { nodes, edges, artists };
}

export const TASTE_GRAPH: TasteGraphResponse = buildGraph();
