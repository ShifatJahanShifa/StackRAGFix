import { searchVectorStore } from "./vectorStore.js";

export async function searchCodebase(query: string) {
  const results = await searchVectorStore(query, 3);
  return results.map(r => ({
    source: r.metadata?.source,
    snippet: r.pageContent.slice(0, 300)
  }));
}
