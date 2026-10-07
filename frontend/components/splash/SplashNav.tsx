import Link from "next/link";
import Wordmark from "@/components/brand/Wordmark";
import SpotifyLoginButton from "@/components/splash/SpotifyLoginButton";

export default function SplashNav() {
  return (
    <header className="mx-auto flex w-full max-w-[1440px] items-center justify-between px-4 py-7 lg:px-16">
      <Link
        href="/"
        className="focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive"
      >
        <Wordmark theme="light" className="h-[30px] w-auto" />
      </Link>
      <div className="flex items-center gap-9">
        <a
          href="#how-it-works"
          className="hidden text-base text-olive focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive md:inline-block"
        >
          How it works
        </a>
        <a
          href="#about"
          className="hidden text-base text-olive focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-olive md:inline-block"
        >
          About
        </a>
        <SpotifyLoginButton size="sm" />
      </div>
    </header>
  );
}
