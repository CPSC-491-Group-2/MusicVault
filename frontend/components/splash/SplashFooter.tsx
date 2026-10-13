import LogoMark from "@/components/brand/LogoMark";
import Wordmark from "@/components/brand/Wordmark";

export default function SplashFooter() {
  return (
    <footer
      id="about"
      className="scroll-mt-8 border-t border-blush/15 bg-olive pt-7 pb-10"
    >
      <div className="mx-auto flex w-full max-w-[1440px] flex-wrap items-end justify-between gap-y-4 px-4 lg:px-16">
        <div className="flex items-end gap-[14px]">
          <LogoMark color="orchid" className="h-[30px] w-auto" />
          <Wordmark theme="dark" className="h-6 w-auto" />
        </div>

        <p className="text-[14px] text-blush/70">
          A CSUF senior capstone project. Not affiliated with Spotify.
        </p>
      </div>
    </footer>
  );
}
