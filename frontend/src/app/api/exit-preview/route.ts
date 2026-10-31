import { draftMode } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const draft = await draftMode();
  draft.disable();

  const response = NextResponse.redirect(new URL("/", request.url));
  response.cookies.delete("wagtail_preview");
  return response;
}
