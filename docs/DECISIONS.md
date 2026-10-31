# Decisions

Recorded decisions for the Wagtail + Next.js CMS. Update this file whenever a
decision changes or a dependency is added.

## Architecture

- **D1 Monorepo:** `site/backend` (Django/Wagtail) and `site/frontend` (Next.js)
  in one git repository.
- **D2 Versions:** Python 3.13, Django 5.2 LTS, Wagtail 7.4 LTS, Wagtail API v2.
  Do not build on the Wagtail 8.0 v3 preview.
- **D3 Types:** The frontend owns Zod schemas per block plus page/settings
  schemas. Backend sample responses are checked by contract tests.
- **D4 Rich text:** Wagtail returns HTML. Backend sanitizes with `nh3`; frontend
  parses sanitized HTML with `html-react-parser` and an allowlist. No
  `dangerouslySetInnerHTML`.
- **D5 Admin origin:** Admin on `cms.example.com`; public frontend on the main
  domain.
- **D6 Preview:** `wagtail-headless-preview` 0.9, `REDIRECT_ON_PREVIEW=True`,
  `PagePreview` API, Next.js Draft Mode.
- **D7 Delete permissions:** Delete is admin-only. Authority is
  `AdminDeleteGuardMiddleware`, blocking every non-superuser on admin `/delete/`
  routes (pages, images, documents, snippets, bulk) for GET and POST.
  `before_delete_page` and `before_bulk_action` provide friendly messages. No
  monkey-patching of Wagtail's image permission policy
  (`register_permission_policy` is 8.0+). There is no native trash, so deletes
  are permanent.
- **D8 Revisions:** Keep the latest 50 revisions plus the live revision (and
  scheduled/in-moderation revisions); prune on publish and via a periodic job.
- **D9 Site host:** `Site` hostname is the public frontend domain; API calls pass
  `?site=<host>` so the API resolves the site while the request goes to the
  backend host.
- **D10 Site settings:** Custom public `GET /api/site/` endpoint returning
  header, footer and theme with image renditions; invalidated by the `settings`
  cache tag.
- **D11 Trailing slash:** Next.js `trailingSlash: false`; normalize internal
  paths to no trailing slash except `/`.
- **D12 Page model:** One `ContentPage` model for `home` and children.
  `can_create_at` is a classmethod allowing creation only under depth-2
  (`home`); `home` is created by `seed_content`, which also removes Wagtail's
  default Welcome page. Only one `home` slug is allowed.
- **D13 Editors group:** Code-managed in `cms/permissions.py` via a
  `post_migrate` handler. Wagtail's image policy checks the swapped image
  model's `permission_policy.auth_model`, which is `wagtailimages.Image` (not
  `cms.CustomImage`). Grant `add_image`, `change_image`, and `choose_image` on
  that content type; the custom model only has
  `add_customimage`/`change_customimage`/`delete_customimage`/
  `view_customimage`, and there is no `choose_customimage`. The handler fails
  loudly if a required row is missing.
- **D14 Revalidation timing:** Webhooks are sent with `transaction.on_commit` so
  Next.js never refetches pre-commit data.
- **D15 API v2 page fields:** Page list/detail responses put `slug`,
  `seo_title`, `search_description`, `type`, `html_url`, and
  `first_published_at` under `meta`; only `id`, `title`, `url_path`, custom
  fields, and StreamField `body` are top-level. The frontend contract reads
  `meta` and must not assume the flat shape shown in the README draft.
- **D16 Draft Mode caching:** With Next 16.4.3 `cacheComponents: false`, a route
  that calls `draftMode()` still builds as static. Public requests are served
  from the static cache (`x-nextjs-cache: HIT`, `s-maxage`), while requests with
  the `__prerender_bypass` cookie re-render the draft payload with
  `Cache-Control: private, no-cache, no-store`.

## Environment and tooling

- **E1 Local Postgres port:** A native PostgreSQL service already listens on
  5432. Docker Compose runs `postgres:16` on **5433** instead; `DATABASE_URL`
  points at 5433. Owner approved this deviation during Phase 0.
- **E2 Pinned tooling:** Python 3.13.17, uv 0.13.6, Node 22.19.0, pnpm 11.5.2.
- **E3 Pinned frontend:** Next.js 16.4.3 (App Router), React 19.3.0, Tailwind CSS
  4.3.3, Zod 4.6.7.
- **E4 Pinned backend:** Django 5.2.18, Wagtail 7.4.4,
  `wagtail-headless-preview` 0.9.0, `nh3` 0.3.7, psycopg 3.3.6.

## Dependencies added beyond the plan

_None yet._

## Phase 0 verification results

**Completed 2026-10-30.** The gate ran against Django 5.2.18, Wagtail 7.4.4,
and Next 16.4.3. Docker/PostgreSQL were unavailable, so backend probes used
SQLite; re-run the backend suite against PostgreSQL in CI before release.

Confirmed from installed 7.4.4 / Next 16.4.3:

- Autosave interval defaults to 500 ms; saving creates a draft revision.
- Preview sizes are 375/768/1280 px; preview auto-update defaults to 500 ms.
- Wagtail 7.4 has no trash/recycle implementation.
- Image `delete` is equivalent to `change` (`CollectionOwnershipPermissionPolicy`); the admin still uses `/delete/` URLs, so the middleware is required.
- Single/bulk URLs use `/admin/pages/<id>/delete/` and `/admin/bulk/<app>/<model>/<action>/`; `/admin/images/<id>/delete/`, `/admin/images/multiple/<id>/delete/`, and `/admin/bulk/cms/customimage/delete/`.
- Hooks: `before_delete_page(request, page)`, `after_delete_page(request, page)`, `before_bulk_action(request, action_type, objects, action)`.
- No `before_delete_image`/`before_delete_document` hooks; use `post_delete` signals or the middleware.
- `AdminDeleteGuardMiddleware` prototype blocked editor GET and POST on single page/image/document delete and on bulk page/custom-image delete; an admin received 200 on the page delete confirmation.
- Custom image permissions: `add_customimage`, `change_customimage`, `delete_customimage`, `view_customimage`; `GroupPagePermission` has `group`, `page`, `permission` FK.
- The image policy's `auth_model` is `wagtailimages.Image`; granting only custom-image rows left add/change/choose false, while granting `add_image`/`change_image`/`choose_image` enabled add/change/choose and still denied delete (D13).
- `ensure_editors_group` ran on a truly fresh SQLite database and normalized page permissions to `add_page`/`change_page`/`publish_page`, collection permissions to `add_image`/`change_image`/`choose_image`, and group permissions to `access_admin`.
- An editor could list images, upload an image (302), edit it (200), and open the image chooser (200), but could not delete images through the admin.
- Welcome is removed; `Site.hostname=localhost`, `port=80`; `?site=localhost` works and `hostname:port` is supported.
- Bulk image upload without `alt` returns a follow-up edit form containing `alt`; no `ValueError`.
- `PagePreview.created_at` is a `DateField`; the package calls `garbage_collect()` on preview (older than yesterday). A `TimestampSigner(salt="headlesspreview.token")` token round-tripped at runtime.
- Old-path revalidation survives a slug change: the signal reported `old_path="/"` and `new_path="/renamed-home"` before the names changed to `/home/`/`/renamed-home/`.
- Revision pruning prototype kept the live, latest, latest-50, and scheduled revisions and deleted older ones.
- `RedirectsAPIViewSet` exposes `old_path` and `location`; auto-created redirects are on by default.
- `publish_scheduled --dryrun` exits 0.
- Native rich text API returns `linktype="page"`; implementation must use the README `SanitizedRichTextBlock.get_api_representation` (expand then `nh3`).
- `/api/site/` (WIP branch) returned `header`, `footer`, and `theme`; logo renditions, nav URL `/`, footer copyright, and theme color were present.
- ContentPage API v2 returns body items as `{type, value, id}`, expanded rich-text links, nested feature values, and `meta.slug`/`meta.seo_title`/`meta.search_description` (D15).
- Next 16.4.3 `revalidateTag(tag, profile)` requires the second argument; `revalidatePath` is unchanged.
- A `draftMode()` route built as static with `cacheComponents: false`: public requests were `x-nextjs-cache: HIT` with `s-maxage=31536000`, while the bypass-cookie request rendered draft content with `private, no-cache, no-store` (D16).
- The frontend Zod contract fixture at `src/lib/contracts/pages.json` parses the real `meta` envelope and all four block envelopes; Vitest, lint, typecheck, and build pass.

WIP restore notes: the parked `cms/permissions.py` references the nonexistent
`choose_customimage` and the parked models have no migration. Fix both before
continuing Phase 1.
