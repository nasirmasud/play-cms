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
  `post_migrate` handler. Image permissions are looked up on the custom image
  model's content type; the handler fails loudly if they are missing.
- **D14 Revalidation timing:** Webhooks are sent with `transaction.on_commit` so
  Next.js never refetches pre-commit data.

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

**Paused 2026-10-29 during the gate; Phase 1 not started.**

Confirmed from installed 7.4.4 / Next 16.4.3:

- Autosave interval defaults to 500 ms; saving creates a draft revision.
- Preview sizes are 375/768/1280 px; preview auto-update defaults to 500 ms.
- Wagtail 7.4 has no trash/recycle implementation.
- Image `delete` is equivalent to `change` (`CollectionOwnershipPermissionPolicy`); the admin still uses `/delete/` URLs, so the middleware is required.
- Single/bulk URLs use `/admin/pages/<id>/delete/` and `/admin/bulk/<app>/<model>/<action>/`; `/admin/images/<id>/delete/`, `/admin/images/multiple/<id>/delete/`, and `/admin/bulk/cms/customimage/delete/`.
- Hooks: `before_delete_page(request, page)`, `after_delete_page(request, page)`, `before_bulk_action(request, action_type, objects, action)`.
- No `before_delete_image`/`before_delete_document` hooks; use `post_delete` signals or the middleware.
- Custom image permissions: `add_customimage`, `change_customimage`, `delete_customimage`, `view_customimage`; `GroupPagePermission` has `group`, `page`, `permission` FK.
- Welcome is removed; `Site.hostname=localhost`, `port=80`; `?site=localhost` works and `hostname:port` is supported.
- Bulk image upload without `alt` returns a follow-up edit form containing `alt`; no `ValueError`.
- `PagePreview.created_at` is a `DateField`; the package calls `garbage_collect()` on preview (older than yesterday).
- `RedirectsAPIViewSet` exposes `old_path` and `location`; auto-created redirects are on by default.
- `publish_scheduled --dryrun` exits 0.
- Native rich text API returns `linktype="page"`; implementation must use the README `SanitizedRichTextBlock.get_api_representation` (expand then `nh3`).
- Next 16.4.3 `revalidateTag(tag, profile)` requires the second argument; `revalidatePath` is unchanged.
- Next build marks a `draftMode()` route static with `cacheComponents: false`; the bypass-cookie runtime check is still pending.

Pending: preview redirect/token runtime; delete middleware prototype; `ensure_editors_group` fresh DB; old-path revalidation; revision pruning; `/api/site/`; ContentPage/Zod contract; final gate table and doc decisions.
