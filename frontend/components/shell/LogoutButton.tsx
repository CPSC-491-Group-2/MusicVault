
"use client";

import { useState } from "react";

import { logoutAccount } from "../../lib/auth";

export function LogoutButton() {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogout() {
    if (isLoggingOut) return;

    setIsLoggingOut(true);
    setError(null);

    try {
      await logoutAccount();

      // Reload into the public login page after the session is cleared.
      window.location.replace("/login");
    } catch {
      setError("Could not log out. Please try again.");
      setIsLoggingOut(false);
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={handleLogout}
        disabled={isLoggingOut}
        className="rounded-lg border border-olive/20 px-3 py-2 text-sm font-medium text-olive transition hover:bg-olive/10 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoggingOut ? "Logging out..." : "Log out"}
      </button>

      {error && (
        <p role="alert" className="mt-2 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
