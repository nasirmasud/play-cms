import { z } from "zod";

export const linkSchema = z
  .object({
    label: z.string(),
    url: z.string(),
    new_tab: z.boolean(),
  })
  .nullable()
  .optional();

export const imageSchema = z
  .object({
    id: z.number(),
    alt: z.string(),
    width: z.number(),
    height: z.number(),
    focal_point: z.object({ x: z.number(), y: z.number() }),
    renditions: z.record(z.string(), z.string()),
  })
  .nullable();

const spacingSchema = z.enum(["sm", "md", "lg"]);
const alignSchema = z.enum(["left", "center", "right"]);

export const textBlockSchema = z.object({
  type: z.literal("text"),
  id: z.string(),
  value: z.object({
    heading: z.string().optional(),
    content: z.string(),
    align: alignSchema,
    max_width: spacingSchema,
    spacing: spacingSchema,
  }),
});

export const heroBlockSchema = z.object({
  type: z.literal("hero"),
  id: z.string(),
  value: z.object({
    heading: z.string(),
    badge_text: z.string().optional(),
    subheading: z.string().optional(),
    image: imageSchema.optional(),
    cta: linkSchema,
    secondary_cta: linkSchema,
    align: alignSchema,
    size: z.enum(["md", "lg", "xl"]),
    background: z.enum(["none", "muted", "primary", "image"]),
    spacing: spacingSchema,
  }),
});

export const featuresBlockSchema = z.object({
  type: z.literal("features"),
  id: z.string(),
  value: z.object({
    heading: z.string().optional(),
    badge_text: z.string().optional(),
    items: z.array(
      z.object({
        icon: z.enum([
          "star",
          "zap",
          "shield",
          "heart",
          "check",
          "sparkles",
          "globe",
          "rocket",
          "layers",
          "settings",
        ]),
        heading: z.string(),
        description: z.string(),
      }),
    ),
    columns: z.enum(["2", "3", "4"]),
    background: z.enum(["none", "muted", "primary"]),
    spacing: spacingSchema,
  }),
});

export const ctaBlockSchema = z.object({
  type: z.literal("cta"),
  id: z.string(),
  value: z.object({
    heading: z.string(),
    subheading: z.string().optional(),
    cta: linkSchema,
    variant: z.enum(["solid", "outline", "gradient"]),
    background: z.enum(["none", "muted", "primary"]),
    align: alignSchema,
  }),
});

export const blockSchema = z.discriminatedUnion("type", [
  heroBlockSchema,
  textBlockSchema,
  featuresBlockSchema,
  ctaBlockSchema,
]);

export const pageMetaSchema = z
  .object({
    slug: z.string(),
    seo_title: z.string().nullable().optional(),
    search_description: z.string().nullable().optional(),
    type: z.string(),
    html_url: z.string(),
    first_published_at: z.string().nullable().optional(),
  })
  .passthrough();

export const pageSchema = z
  .object({
    id: z.number(),
    title: z.string(),
    url_path: z.string(),
    meta: pageMetaSchema,
    og_image: imageSchema.optional(),
    body: z.array(blockSchema),
  })
  .passthrough();

export type Page = z.infer<typeof pageSchema>;
export type Block = z.infer<typeof blockSchema>;
