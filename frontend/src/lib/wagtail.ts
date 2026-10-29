import { env } from "./env";

export type WagtailPage = {
  id: number;
  title: string;
  slug: string;
  meta: {
    type: string;
    html_url: string;
    slug: string;
    first_published_at: string | null;
  };
};

type PagesResponse = {
  items: WagtailPage[];
};

type PagesQuery = {
  type?: string;
  slug?: string;
  fields?: string[];
  limit?: number;
  site?: string;
};

export function buildPagesUrl(query: PagesQuery = {}): string {
  const url = new URL("/api/v2/pages/", env.WAGTAIL_API_URL);
  url.searchParams.set("site", query.site ?? env.WAGTAIL_SITE_HOST);

  if (query.type) {
    url.searchParams.set("type", query.type);
  }
  if (query.slug) {
    url.searchParams.set("slug", query.slug);
  }
  if (query.fields?.length) {
    url.searchParams.set("fields", query.fields.join(","));
  }
  if (query.limit) {
    url.searchParams.set("limit", String(query.limit));
  }

  return url.toString();
}

export async function fetchPageBySlug(
  slug: string,
  type?: string,
): Promise<WagtailPage | null> {
  const response = await fetch(
    buildPagesUrl({ slug, type, fields: ["title", "slug"] }),
    { cache: "no-store" },
  );

  if (!response.ok) {
    return null;
  }

  const data = (await response.json()) as PagesResponse;
  return data.items[0] ?? null;
}
