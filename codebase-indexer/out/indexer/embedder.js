import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
const embedder = new HuggingFaceTransformersEmbeddings({
    model: "Xenova/all-MiniLM-L6-v2",
});
// const embedder = new HuggingFaceTransformersEmbeddings({
//   modelName: "sentence-transformers/all-MiniLM-L6-v2",
// });
export async function generateEmbedding(content) {
    const [embedding] = await embedder.embedDocuments([content]);
    return embedding;
}
//# sourceMappingURL=embedder.js.map