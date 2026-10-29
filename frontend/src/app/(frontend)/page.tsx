import { fetchPageBySlug } from "@/lib/wagtail";

export const dynamic = "force-dynamic";

export default async function Home() {
  let page = null;
  let apiError = false;

  try {
    page = await fetchPageBySlug("home");
  } catch {
    apiError = true;
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 px-6 py-24">
      <p className="text-sm font-medium uppercase tracking-widest text-zinc-500">
        Headless Wagtail CMS
      </p>
      <h1 className="text-4xl font-semibold tracking-tight">
        {page ? page.title : "Home page not available"}
      </h1>
      {apiError ? (
        <p className="text-zinc-600">
          The Wagtail API is not reachable. Start the backend on
          http://localhost:8000 and reload.
        </p>
      ) : page ? (
        <p className="text-zinc-600">
          Loaded page <code>{page.slug}</code> from the Wagtail API.
        </p>
      ) : (
        <p className="text-zinc-600">
          No live page with slug <code>home</code> was found.
        </p>
      )}
    </main>
  );
}
