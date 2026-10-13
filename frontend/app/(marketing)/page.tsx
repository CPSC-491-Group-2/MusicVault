import Hero from "@/components/splash/Hero";
import HowItWorks from "@/components/splash/HowItWorks";
import Moods from "@/components/splash/Moods";
import PopularityRow from "@/components/splash/PopularityRow";
import SplashFooter from "@/components/splash/SplashFooter";
import SplashNav from "@/components/splash/SplashNav";

export default function SplashPage() {
  return (
    <>
      <SplashNav />

      <main>
        <Hero />
        <PopularityRow />
        <Moods />
        <HowItWorks />
      </main>

      <SplashFooter />
    </>
  );
}
