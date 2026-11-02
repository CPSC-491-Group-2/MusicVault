
import Link from "next/link";

import Wordmark from "@/components/brand/Wordmark";
import SpotifyLoginButton from "@/components/splash/SpotifyLoginButton";

export default function SignupPage() {
  return (
    <main className="flex min-h-dvh items-center justify-center bg-canvas px-5 py-12">
      <div className="w-full max-w-md rounded-2xl border border-black/10 bg-white p-8 shadow-sm">
        <Link href="/" className="inline-block">
          <Wordmark theme="light" className="h-7 w-auto" />
        </Link>

        <h1 className="mt-8 text-3xl font-semibold tracking-tight">
          Create your MusicVault account
        </h1>

        <p className="mt-3 text-sm text-neutral-600">
          Start building your music profile and discovering songs
          that match your taste.
        </p>

        <form className="mt-8 space-y-5">
          <div>
            <label
              htmlFor="display_name"
              className="mb-2 block text-sm font-medium"
            >
              Display name
            </label>
            <input
              id="display_name"
              name="display_name"
              type="text"
              autoComplete="name"
              placeholder="MusicFan"
              disabled
              className="w-full rounded-lg border border-neutral-300 px-4 py-3 text-sm disabled:opacity-50"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="mb-2 block text-sm font-medium"
            >
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              disabled
              className="w-full rounded-lg border border-neutral-300 px-4 py-3 text-sm disabled:opacity-50"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-2 block text-sm font-medium"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              placeholder="Create a password"
              disabled
              className="w-full rounded-lg border border-neutral-300 px-4 py-3 text-sm disabled:opacity-50"
            />
          </div>

          <p className="text-sm text-neutral-600">
            Email registration will be available once password
            security integration is complete.
          </p>

          <button
            type="button"
            disabled
            className="w-full rounded-lg bg-neutral-800 px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            Create account
          </button>
        </form>

        <div className="mt-8 border-t border-neutral-200 pt-6">
          <p className="mb-4 text-center text-sm text-neutral-600">
            Or use Spotify to access MusicVault
          </p>

          <SpotifyLoginButton size="lg" />
        </div>

        <p className="mt-8 text-center text-sm text-neutral-600">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-semibold underline underline-offset-4"
          >
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
