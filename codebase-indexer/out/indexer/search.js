import { searchVectorStore } from "./vectorStore.js";
export async function searchCodebase(query) {
    const results = await searchVectorStore(query, 3);
    return results.map(r => ({
        source: r.metadata?.source,
        snippet: r.pageContent.slice(0, 300)
    }));
}
//# sourceMappingURL=search.js.map