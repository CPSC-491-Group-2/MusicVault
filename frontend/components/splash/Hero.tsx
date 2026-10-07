import Image from "next/image";
import SpotifyLoginButton from "@/components/splash/SpotifyLoginButton";

export default function Hero() {
  return (
    <section className="mx-auto w-full max-w-[1440px] px-4 pt-14 pb-30 lg:px-16">
      <div className="grid items-center gap-[72px] lg:grid-cols-2">
        <div>
          <h1 className="text-[48px] font-semibold leading-[0.98] tracking-[-0.035em] lg:text-[80px]">
            Music you&apos;d love, from artists you haven&apos;t heard yet.
          </h1>
          <p className="mt-6 max-w-[520px] text-[21px] leading-[1.45]">
            Connect your Spotify account and MusicVault recommends songs that
            fit your taste, weighted toward smaller artists and tracks the
            charts skip.
          </p>
          <SpotifyLoginButton size="lg" className="mt-10" />
        </div>
        <div className="aspect-[4/5] w-full lg:aspect-auto lg:h-[680px] lg:w-[600px]">
          <Image
            src="/images/splash/hero.jpg"
            width={600}
            height={680}
            alt="A home studio with guitars in afternoon light"
            priority
            className="h-full w-full rounded-[20px] object-cover"
          />
        </div>
      </div>
    </section>
  );
}
