// src/indexer/vectorStore.ts
 import { Chroma } from "@langchain/community/vectorstores/chroma";
// import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import path from "path";
import os from "os";

import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";

const embedder = new HuggingFaceTransformersEmbeddings({
    model: "Xenova/all-MiniLM-L6-v2",
});
let vectorStore: Chroma | null = null;

// Initialize Chroma with local persistent storage
export async function getVectorStore(): Promise<Chroma> {
  if (!vectorStore) {
    const persistDir = path.join(os.homedir(), ".stackrag_index");
    // const embeddings = new OpenAIEmbeddings({ modelName: "text-embedding-3-small" });

    vectorStore = await Chroma.fromExistingCollection(embedder, {
      collectionName: "codebase",
      url: "http://localhost:8000", // optional, only if using Chroma server
      // For local persistence: if serverless mode
      collectionMetadata: { persistDir }
    });
  }
  return vectorStore;
}

export async function addToVectorStore(filePath: string, content: string) {
  const store = await getVectorStore();
  await store.addDocuments([{ pageContent: content, metadata: { source: filePath } }]);
}

export async function searchVectorStore(query: string, k = 3) {
  const store = await getVectorStore();
  const results = await store.similaritySearch(query, k);
  return results;
}
