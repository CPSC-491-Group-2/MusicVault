import Link from "next/link";

import Wordmark from "@/components/brand/Wordmark";
import SpotifyLoginButton from "@/components/splash/SpotifyLoginButton";

export default function LoginPage() {
  return (
    <main className="flex min-h-dvh items-center justify-center bg-canvas px-5 py-12">
      <div className="w-full max-w-md rounded-2xl border border-black/10 bg-white p-8 shadow-sm">
        <Link href="/" className="inline-block">
          <Wordmark theme="light" className="h-7 w-auto" />
        </Link>

        <h1 className="mt-8 text-3xl font-semibold tracking-tight">
          Log in to MusicVault
        </h1>

        <p className="mt-3 text-sm text-neutral-600">
          Welcome back! Choose how you would like to
          access your MusicVault account.
        </p>

        <div className="mt-8">
          <SpotifyLoginButton size="lg" />
        </div>

        <div className="mt-8 border-t border-neutral-200 pt-6">
          <h2 className="text-base font-semibold">
            Email and password login
          </h2>

          <p className="mt-2 text-sm text-neutral-600">
            Local account authentication is currently
            being developed and is not yet available.
          </p>
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/"
            className="text-sm font-medium underline underline-offset-4"
          >
            Return to home
          </Link>
        </div>
      </div>
    </main>
  );
}