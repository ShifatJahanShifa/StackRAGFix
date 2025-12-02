import { DefaultEmbeddingFunction } from "@chroma-core/default-embed";
import { ChromaClient } from "chromadb";
const client = new ChromaClient({
    host: "localhost",
    port: 9000
});
// using default embedding function. Default: all-MiniLM-L6-v2
export const getCollection = async (collectionName) => {
    const collection = await client.getOrCreateCollection({
        name: collectionName,
        configuration: {
            'embeddingFunction': new DefaultEmbeddingFunction({
                modelName: "Xenova/all-MiniLM-L6-v2"
            }),
            'hnsw': {
                space: 'cosine'
            }
        }
    });
    return collection;
};
