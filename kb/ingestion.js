import 'dotenv/config';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { Chroma } from '@langchain/community/vectorstores/chroma';
import { MistralAIEmbeddings } from '@langchain/mistralai';
import fs from 'fs';
import { CHUNK_SIZE, CHUNK_OVERLAP, PYTHON_QA_COLLECTION, JAVASCRIPT_QA_COLLECTION, MODEL } from './constants/vector_store';

const PYTHON_OUTPUT_FILE = "stackoverflow_python_questions.json"
const JAVASCRIPT_OUTPUT_FILE = "stackoverflow_javascript_questions.json"
const LANGUAGE = "python"
const apiKey = "api-key-will-be-configured-later";

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: CHUNK_SIZE,
  chunkOverlap: CHUNK_OVERLAP,
  separators: ["\n\n", "\n", " ", ""],
});

const embeddings = new MistralAIEmbeddings({
  apiKey: apiKey,
  model: MODEL,
});

// TODO: switch the collection between python and javascript.
let qa_collection = PYTHON_QA_COLLECTION;


async function main(language) {
    try {
        const qa_threads = language===LANGUAGE ? JSON.parse(fs.readFileSync(PYTHON_OUTPUT_FILE, 'utf-8')) : JSON.parse(fs.readFileSync(JAVASCRIPT_OUTPUT_FILE, 'utf-8'));
        
       await create_knowledge_base(qa_threads, qa_collection);
        
    } catch (error) {
        console.error("Error processing JSON file:", error);
    }


    async function create_knowledge_base(threads, collectionName) {
        const SO_collection = threadToDocument(threads);
        const documents = await processDocuments(SO_collection);
        const vectordb = await storeInVectorDB(documents, collectionName);
        return vectordb;
        }
}

function threadToDocument(threads) {
    const SO_collection = [];

    for (const thread of threads) {
        const questionId = thread.question_id;
        const title = thread.title;
        const body = thread.question_body;

        const questionDoc = {
            pageContent: `Question: ${title}\n\n${body}`,
            metadata: {
                type: "question",
                question_id: questionId,
                title: title,
                score: thread.score || 0,
                tags: (thread.tags || []).join(","),
                link: thread.link || "",
                view_count: thread.view_count || 0,
                answer_count: thread.answer_count || 0,
            },
        };
        SO_collection.push(questionDoc);

        if (thread.answers) {
            for (const answer of thread.answers) {
                    const answerDoc = {
                    pageContent: `Answer: ${answer.body}`,
                    metadata: {
                        type: "answer",
                        question_id: questionId,
                        score: answer.score,
                    },
                };
                SO_collection.push(answerDoc);
            }
        }
    }
    return SO_collection;
}

async function processDocuments(documents) {
    console.log(`Splitting ${documents.length} documents...`);
    const finalDocs = [];

    for (const doc of documents) {
        try {
        const splitDocs = await textSplitter.splitDocuments([doc]);
        finalDocs.push(...splitDocs);
        } catch (error) {
        console.error("Error splitting document:", error.message);
        }
    }

    console.log(`Split into ${finalDocs.length} chunks`);
    return finalDocs;
}

async function storeInVectorDB(finalDocs, collectionName) {
    // Store in ChromaDB with batching
    console.log(`Storing documents in ChromaDB for ${collectionName}...`);

    try {
        const initDocs = finalDocs.slice(0, 1);
        let vectorStore = await Chroma.fromDocuments(initDocs, embeddings, {
            collectionName: collectionName,
            host: "localhost",
            port: 9000,
            ssl: false,
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
            console.error(`Error processing batch: ${batchError.message}`);
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
                console.error(
                `Could not process document ${j + 1}: ${docError.message}`
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
main("python");