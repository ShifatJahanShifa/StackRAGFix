import { Chroma } from "@langchain/community/vectorstores/chroma";
import { MistralAIEmbeddings } from "@langchain/mistralai";
import "dotenv/config";
const apiKey = "api-key";
const embeddings = new MistralAIEmbeddings({
    apiKey,
    model: "mistral-embed",
});
const COLLECTION = "INPUTS";
async function runRetrieval() {
    console.log("Connecting to Chroma collection:", COLLECTION);
    // Load existing stored vectorstore
    const vectorStore = await Chroma.fromExistingCollection(embeddings, {
        collectionName: COLLECTION,
    });
    console.log("Connected. Running retrieval tests...");
    // ---------------------------------------------------
    // 1. SIMPLE SIMILARITY SEARCH
    // ---------------------------------------------------
    const query = "how to print name or greeting in python?";
    console.log("\n🔍 Query:", query);
    const results = await vectorStore.similaritySearch(query, 3);
    console.log("\n📌 Top 3 results:");
    for (const res of results) {
        console.log("----");
        console.log("Content:", res.pageContent);
        console.log("Metadata:", res.metadata);
    }
    // ---------------------------------------------------
    // 2. USING RETRIEVER
    // ---------------------------------------------------
    const retriever = vectorStore.asRetriever({
        k: 3,
        filter: {
            type: "function"
        }
    });
    const retrievedDocs = await retriever._getRelevantDocuments(query);
    console.log("\n📌 Retriever returned these documents:");
    for (const d of retrievedDocs) {
        console.log("----");
        console.log("Content:", d.pageContent);
        console.log("Metadata:", d.metadata);
    }
}
runRetrieval().catch(console.error);
