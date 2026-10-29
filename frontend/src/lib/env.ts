import { z } from "zod";

const envSchema = z.object({
  WAGTAIL_API_URL: z.url().default("http://localhost:8000"),
  WAGTAIL_SITE_HOST: z.string().min(1).default("localhost"),
  NEXT_PUBLIC_SITE_URL: z.url().default("http://localhost:3000"),
});

export const env = envSchema.parse({
  WAGTAIL_API_URL: process.env.WAGTAIL_API_URL,
  WAGTAIL_SITE_HOST: process.env.WAGTAIL_SITE_HOST,
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
});
