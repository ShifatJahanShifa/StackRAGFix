import { ChromaClient } from "chromadb";
const client = new ChromaClient();
let collectionName = "INPUTS";
try {
    await client.deleteCollection({ name: collectionName });
    console.log("Old collection deleted:", collectionName);
}
catch (err) {
    console.log("No existing collection found. Creating new one.");
}
