import { v4 as uuidv4 } from 'uuid';
import { Metadata } from 'chromadb';
import 'dotenv/config';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { MistralAIEmbeddings } from '@langchain/mistralai';
import fs from 'fs';



const apiKey = "api-key";

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1500,
  chunkOverlap: 200,
  separators: ["\n\n", "\n", " ", ""],
});

const embeddings = new MistralAIEmbeddings({
  apiKey: apiKey,
  model: "mistral-embed",
});

let collection = "INPUTS";


async function main(jsonFile: string) {
  try {
    const codeChunks = JSON.parse(fs.readFileSync(jsonFile, 'utf-8'));
    
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
//   console.log('gg, ', threads)
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
    let vectorStore = await Chroma.fromDocuments(initDocs, embeddings, {
      collectionName: collectionName,
    // //   host: "localhost",
    //   port: 8000,
    //   ssl: false,
      collectionMetadata: {
        "hnsw:space": "cosine",
      },
    });

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

let jsCodeChunks = "jsCodeChunks.json";
let pyCodeChunks = "pyCodeChunks.json";
await main(jsCodeChunks)
await main(pyCodeChunks)