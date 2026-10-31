import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { buildPagesUrl, getPreviewPage } from "./wagtail";

const previewPage = {
  id: 1,
  title: "Preview",
  url_path: "/home/preview/",
  meta: {
    slug: "preview",
    type: "cms.ContentPage",
    html_url: "http://localhost:3000/preview",
    seo_title: null,
    search_description: null,
  },
  body: [
    {
      type: "hero",
      id: "b1",
      value: {
        heading: "Hi",
        align: "center",
        size: "lg",
        background: "none",
        spacing: "md",
      },
    },
  ],
};

const jsonResponse = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json" } });

describe("buildPagesUrl", () => {
  it("builds a site-scoped pages URL", () => {
    const url = new URL(
      buildPagesUrl({
        type: "home.HomePage",
        slug: "home",
        fields: ["title", "slug"],
      }),
    );

    expect(url.origin).toBe("http://localhost:8000");
    expect(url.pathname).toBe("/api/v2/pages/");
    expect(url.searchParams.get("site")).toBe("localhost");
    expect(url.searchParams.get("type")).toBe("home.HomePage");
    expect(url.searchParams.get("slug")).toBe("home");
    expect(url.searchParams.get("fields")).toBe("title,slug");
  });
});

describe("getPreviewPage", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the parsed page on a valid token", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      jsonResponse(previewPage),
    );

    const page = await getPreviewPage("cms.contentpage", "valid-token");

    expect(page).toEqual(previewPage);
    expect(fetch).toHaveBeenCalledTimes(1);
    const calledUrl = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][0];
    expect(String(calledUrl)).toContain("/api/v2/page_preview/0/");
    expect(String(calledUrl)).toContain("content_type=cms.contentpage");
    expect(String(calledUrl)).toContain("token=valid-token");
  });

  it("returns null on 401", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(jsonResponse({}, 401));
    expect(await getPreviewPage("cms.contentpage", "bad")).toBeNull();
  });

  it("returns null on 403", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(jsonResponse({}, 403));
    expect(await getPreviewPage("cms.contentpage", "tampered")).toBeNull();
  });

  it("returns null on 404", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(jsonResponse({}, 404));
    expect(await getPreviewPage("cms.contentpage", "missing")).toBeNull();
  });

  it("throws on 5xx", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(jsonResponse({}, 500));
    await expect(getPreviewPage("cms.contentpage", "token")).rejects.toThrow(
      /Wagtail preview API/,
    );
  });

  it("returns null when the payload fails validation", async () => {
    (fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      jsonResponse({ not: "a page" }),
    );
    expect(await getPreviewPage("cms.contentpage", "token")).toBeNull();
  });
});
