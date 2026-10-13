const STEPS = [
  {
    title: "Connect Spotify",
    body: "We read your top tracks, saved songs, and playlists. MusicVault never posts or changes anything on your account.",
  },
  {
    title: "Pick a few songs",
    body: "Choose songs you want more of, or let your listening history do it for you.",
  },
  {
    title: "Get recommendations",
    body: "See songs that match on sound rather than popularity. Save the ones you like, or export them to a playlist or CSV.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-8 bg-olive pt-28 pb-[120px]">
      <div className="mx-auto w-full max-w-[1440px] px-4 lg:px-16">
        <h2 className="text-[44px] font-semibold text-blush">How it works</h2>

        <div className="mt-14 grid grid-cols-1 gap-16 md:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.title}>
              <h3 className="text-[22px] font-medium text-orchid">
                {step.title}
              </h3>

              <p className="mt-3 text-[17px] leading-[1.55] text-blush">
                {step.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
