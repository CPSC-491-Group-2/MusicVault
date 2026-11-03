import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("auth_error");
  const url = new URL("/login", request.url);
  if (code) url.searchParams.set("error", code);
  return NextResponse.redirect(url);
}

export const config = {
  matcher: [{ source: "/", has: [{ type: "query", key: "auth_error" }] }],
};
