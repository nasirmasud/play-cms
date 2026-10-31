import { describe, expect, it } from "vitest";

import { normalizeInternalPath, pagePath } from "./paths";

describe("pagePath", () => {
  it("maps /home/ to /", () => {
    expect(pagePath("/home/")).toBe("/");
  });

  it("maps /home/about/ to /about", () => {
    expect(pagePath("/home/about/")).toBe("/about");
  });

  it("maps /about/ to /about", () => {
    expect(pagePath("/about/")).toBe("/about");
  });

  it("leaves / unchanged", () => {
    expect(pagePath("/")).toBe("/");
  });
});

describe("normalizeInternalPath", () => {
  it("strips trailing slashes except root", () => {
    expect(normalizeInternalPath("/about/")).toBe("/about");
    expect(normalizeInternalPath("/")).toBe("/");
    expect(normalizeInternalPath("/a/b//")).toBe("/a/b");
  });

  it("returns non-path values unchanged", () => {
    expect(normalizeInternalPath("http://example.com/x")).toBe(
      "http://example.com/x",
    );
  });
});
