export function pagePath(urlPath: string): string {
  const parts = urlPath.split("/").filter(Boolean);
  if (parts[0] === "home") parts.shift();
  return parts.length ? `/${parts.join("/")}` : "/";
}

export function normalizeInternalPath(path: string): string {
  if (!path.startsWith("/")) return path;
  if (path === "/") return path;
  return path.replace(/\/+$/, "");
}
