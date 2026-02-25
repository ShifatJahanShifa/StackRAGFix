// import * as dotenv from "dotenv";
// dotenv.config();
import * as vscode from "vscode";
import { processJsFiles } from "./jsChunker";
import { processPythonFiles } from "./pyChunker"
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { MistralAIEmbeddings } from "@langchain/mistralai";
import { CHUNK_OVERLAP, CHUNK_SIZE, MODEL } from "./vector_store"
import { main } from "./codeIngestion";
import path from "path";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { QdrantVectorStore } from '@langchain/qdrant';
import {QdrantClient} from '@qdrant/js-client-rest';
const COLLECTION_PREFIX = "STACKRAG_";

//Load API key from .env
const apiKey = process.env.MISTRAL_API_KEY as string;

const qdrantApiKey = process.env.QDRANT_API_KEY as string;
const qdrantClusterEndpoint = process.env.QDRANT_CLUSTER_ENDPOINT as string;


if (!apiKey) {
    throw new Error("Service: MISTRAL_API_KEY not found in .env");
}

if (!qdrantApiKey) {
    throw new Error("Service: QDRANT_API_KEY not found in .env");
}

if(!qdrantClusterEndpoint) {
    throw new Error("Service: QDRANT_CLUSTER_ENDPOINT not found in .env");
}
const client = new QdrantClient({
    url: qdrantClusterEndpoint,
    apiKey: qdrantApiKey,
})

const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: CHUNK_SIZE,
    chunkOverlap: CHUNK_OVERLAP,
    separators: ["\n\n", "\n", " ", ""],
});

const embeddings = new MistralAIEmbeddings({
    apiKey,
    model: MODEL
});


export async function deleteExistingCollection(workspaceRoot: string) {

    const workspaceName = path.basename(workspaceRoot);
    const collectionName = COLLECTION_PREFIX + workspaceName;

    const vectorStore = await QdrantVectorStore.fromExistingCollection(
        embeddings,
        {
            client,
            collectionName,
        }
    );
    try {
        const qdrantClient = vectorStore.client;
        await qdrantClient.deleteCollection(collectionName);       
        console.log("Collection deleted from Qdrant");
               
    } catch (err) {
        console.log("No existing collection found.");
    }
}


export async function indexWorkspace(
    workspaceRoot: string,
    progressCallback?: (current: number, total: number) => void
) {

    const workspaceName = path.basename(workspaceRoot);
    const collectionName = COLLECTION_PREFIX + workspaceName;

    const files = await vscode.workspace.findFiles(
        "**/*.{py,js}",
        "**/node_modules/**"
    );

    const totalFiles = files.length;
    let processed = 0;

    if (totalFiles === 0) return;

    // Get chunks directly
    const jsChunks = await processJsFiles(workspaceRoot);
    const pyChunks = await processPythonFiles(workspaceRoot);

    const allChunks = [...jsChunks, ...pyChunks];

    await main(allChunks, collectionName)



    // console.log("DEBUG: vectorStore", vectorStore)

    // Progress
    for (let i = 0; i < totalFiles; i++) {
        processed++;
        progressCallback?.(processed, totalFiles);
    }

    console.log(`Indexed ${workspaceName} into ${collectionName}`);
    return totalFiles;
}


export async function retrieveRelevantCode(
    workspaceRoot: string,
    query: string
) {

    const workspaceName = path.basename(workspaceRoot);
    const collectionName = COLLECTION_PREFIX + workspaceName;

    // const vectorStore = await Chroma.fromExistingCollection(
    //     embeddings,
    //     { collectionName }
    // );
    const vectorStore = await QdrantVectorStore.fromExistingCollection(
        embeddings,
        {
            client,
            collectionName,
        }
    );


    const results = await vectorStore.similaritySearch(query, 3);

    return results.map(r => r.pageContent).join("\n\n");
}
