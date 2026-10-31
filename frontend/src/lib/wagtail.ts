import { env } from "./env";

import { pageSchema, type Page } from "./schemas";

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

const API = env.WAGTAIL_API_URL.replace(/\/$/, "");
const PAGE_FIELDS = "body,seo_title,search_description,og_image,url_path";

export function apiUrl(path: string) {
  return `${API}${path}`;
}

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

export async function getPreviewPage(
  contentType: string,
  token: string,
): Promise<Page | null> {
  const params = new URLSearchParams({
    content_type: contentType,
    token,
    fields: PAGE_FIELDS,
  });

  const response = await fetch(apiUrl(`/api/v2/page_preview/0/?${params}`), {
    cache: "no-store",
  });

  if (response.status === 401 || response.status === 403 || response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Wagtail preview API ${response.status}`);
  }

  const data = await response.json();
  const parsed = pageSchema.safeParse(data);
  return parsed.success ? parsed.data : null;
}
