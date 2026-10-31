import { draftMode } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { getPreviewPage } from "@/lib/wagtail";
import { pagePath } from "@/lib/paths";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const contentType = request.nextUrl.searchParams.get("content_type");
  const token = request.nextUrl.searchParams.get("token");

  if (!contentType || !token) {
    return new NextResponse("Missing preview parameters", { status: 400 });
  }

  const page = await getPreviewPage(contentType, token);
  if (!page) {
    return new NextResponse("Invalid or expired preview token", { status: 401 });
  }

  const draft = await draftMode();
  draft.enable();

  const response = NextResponse.redirect(
    new URL(pagePath(page.url_path), request.url),
  );

  response.cookies.set(
    "wagtail_preview",
    JSON.stringify({ contentType, token }),
    {
      httpOnly: true,
      sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60,
    },
  );

  response.headers.set("Referrer-Policy", "no-referrer");
  return response;
}
