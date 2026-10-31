import { describe, expect, it } from "vitest";

import fixture from "./contracts/pages.json";
import { blockSchema, pageSchema } from "./schemas";

describe("Wagtail API v2 contract", () => {
  const page = fixture.items[0];

  it("accepts a ContentPage payload with meta-scoped page fields", () => {
    const parsed = pageSchema.parse(page);

    expect(parsed.meta.slug).toBe("about");
    expect(parsed.meta.seo_title).toBe("About SEO");
    expect(parsed.meta.search_description).toBe("About description");
    expect("slug" in parsed).toBe(false);
  });

  it("accepts every body block envelope", () => {
    for (const block of page.body) {
      expect(blockSchema.parse(block)).toBeTruthy();
    }
  });

  it("rejects a payload without meta", () => {
    const withoutMeta = Object.fromEntries(
      Object.entries(page).filter(([key]) => key !== "meta"),
    );

    expect(pageSchema.safeParse(withoutMeta).success).toBe(false);
  });
});
