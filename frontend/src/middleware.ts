import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Token is stored in localStorage which is not accessible server-side.
  // Route protection is handled client-side in the layout.
  // This middleware handles any cookie-based token if needed in future.
  const token = request.cookies.get("access_token")?.value;

  if (!token && !PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    // Allow the request through — client-side auth will redirect
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
