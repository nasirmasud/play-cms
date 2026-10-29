import { describe, expect, it } from "vitest";

import { buildPagesUrl } from "./wagtail";

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
