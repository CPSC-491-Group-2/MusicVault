// One id scheme shared by the taste graph and the deck pool, so the same real
// song carries the same id wherever it appears.

export function songId(artistSlug: string, title: string): string {
  const titleSlug = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

  return `song:${artistSlug}-${titleSlug}`;
}
