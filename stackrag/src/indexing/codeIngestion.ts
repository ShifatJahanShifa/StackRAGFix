// import { v4 as uuidv4 } from 'uuid';
// import * as dotenv from "dotenv";
// dotenv.config();
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { MistralAIEmbeddings } from '@langchain/mistralai';
import { QdrantVectorStore } from '@langchain/qdrant';
import {QdrantClient} from '@qdrant/js-client-rest';
import { ChromaClient } from "chromadb";
import { CHUNK_SIZE, CHUNK_OVERLAP, MODEL } from './vector_store.js';

const apiKey = process.env.MISTRAL_API_KEY as string;
const qdrantApiKey = process.env.QDRANT_API_KEY as string;
const qdrantClusterEndpoint = process.env.QDRANT_CLUSTER_ENDPOINT as string;

if (!apiKey) {
    throw new Error("Code ingestion: MISTRAL_API_KEY not found in .env");
}

if (!qdrantApiKey) {
    throw new Error("Code ingestion: QDRANT_API_KEY not found in .env");
}

if(!qdrantClusterEndpoint) {
    throw new Error("Code ingestion: QDRANT_CLUSTER_ENDPOINT not found in .env");
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
    apiKey: apiKey,
    model: MODEL,
});



export async function main(codeChunks: any, collection: string) {
    try {
        await create_knowledge_base(codeChunks, collection);
        
    } catch (error) {
        console.error("Error processing JSON file:", error);
    }
    
    
    async function create_knowledge_base(threads: any, collectionName: string) {
        const code_collection = threadToDocument(threads);
        const documents = await processDocuments(code_collection, textSplitter);
        const vectordb = await storeInVectorDB(documents, collectionName);
        return vectordb;
    }
}

function threadToDocument(threads: any) {
    const code_collection: any[] = [];
    for (const chunk of threads) {
        let code=chunk.content;
        let metadataInfo = chunk.metadata;
        
        const codeDoc = {
            pageContent: `Code: ${code}`,
            metadata: {
                filePath: metadataInfo.filePath,
                type: metadataInfo.type,
                extension: metadataInfo.ext,
            },
        };
        code_collection.push(codeDoc);
    }
    return code_collection;
}

async function processDocuments(documents: any, textSplitter: any) {
    console.log(`Splitting ${documents.length} documents...`);
    const finalDocs = [];
    
    for (const doc of documents) {
        try {
            const splitDocs = await textSplitter.splitDocuments([doc]);
            finalDocs.push(...splitDocs);
        } catch (error) {
            if (error instanceof Error) {
                console.error("Error splitting document:", error.message);
            } else {
                console.error("Error splitting document:", error);
            }
        }
    }
    
    console.log(`Split into ${finalDocs.length} chunks`);
    return finalDocs;
}

async function storeInVectorDB(finalDocs: any, collectionName: string) {
    // Store in ChromaDB with batching
    console.log(`Storing documents in ChromaDB for ${collectionName}...`);
    
    try {
        const initDocs = finalDocs.slice(0, 1);
        // const client = new ChromaClient({
        //     host: "localhost", // Note: Some versions prefer just "localhost"
        //     port: 8000
        // });
    
        // let vectorStore = await Chroma.fromDocuments(initDocs, embeddings, {
        //     index: client,
        //     collectionName: collectionName,
        //     collectionMetadata: {
        //         "hnsw:space": "cosine",
        //     },
        // });

        const vectorStore = await QdrantVectorStore.fromDocuments(
            initDocs,
            embeddings,
            {
                client,
                collectionName: collectionName,
                collectionConfig: {
                    vectors: {
                        size: 1024,
                        distance: "Cosine",
                    },
                },
            }
        );

        const remainingDocs = finalDocs.slice(1);
        const batchSize = 200;
        console.log(
        `Processing ${remainingDocs.length} remaining documents in batches of ${batchSize}...`
        );

        for (let i = 0; i < remainingDocs.length; i += batchSize) {
        try {
            const batch = remainingDocs.slice(i, i + batchSize);
            console.log(
            `Processing batch ${Math.floor(i / batchSize) + 1} of ${Math.ceil(
                remainingDocs.length / batchSize
            )}`
            );

            await vectorStore.addDocuments(batch);
            console.log(`Processed batch of ${batch.length} documents`);
            } catch (batchError) {
            console.error(`Error processing batch: ${batchError instanceof Error ? batchError.message : String(batchError)}`);
            console.log("Falling back to processing one document at a time...");

            const batchStart = i;
            const batchEnd = Math.min(i + batchSize, remainingDocs.length);

            for (let j = batchStart; j < batchEnd; j++) {
            try {
                await vectorStore.addDocuments([remainingDocs[j]]);
                console.log(
                `Processed document ${j + 1} of ${remainingDocs.length}`
                );
            } catch (docError) {
                // Normalize unknown error to a string before logging
                let docErrorMessage: string;
                if (docError instanceof Error) {
                docErrorMessage = docError.message;
                } else {
                try {
                    docErrorMessage = JSON.stringify(docError);
                } catch {
                    docErrorMessage = String(docError);
                }
                }
                console.error(
                `Could not process document ${j + 1}: ${docErrorMessage}`
                );
            }
            }
        }

        // Add a small delay between batches to avoid rate limiting
        await new Promise((resolve) => setTimeout(resolve, 1000));
        }

        console.log("Successfully stored all documents in ChromaDB");
        return vectorStore;
    } catch (error) {
        console.error("Error initializing ChromaDB:", error);
        throw error;
    }
}

