import { createReadStream } from 'fs';
import * as readline from 'readline';
import { getCollection } from './chromaCollection.ts';
import { v4 as uuidv4 } from 'uuid';
import { Metadata } from 'chromadb';

let documents: string[] = [];
async function processLines(filePath: string) {
    const stream = createReadStream(filePath, { encoding: 'utf8' });
    const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });

    for await (const line of rl) {
        if(line.length == 0) continue;
        console.log('LINE:', line);
        documents.push(line)
    }
    console.log(documents.length)

    const testingCollection = await getCollection("testing")

    const uuids: string[] = [];
    const metadatas: Metadata[] = [];
    const re = /^\s*\d+\.\s*([^:]+)\s*:\s*(.+)$/;
    for (let i = 0; i < documents.length; i++) {
        uuids.push(uuidv4());
        const match = documents[i].match(re);
        if (match) 
        {
            const name = match[1].trim();           
            metadatas.push({ type: name });         // attach metadata.type = testing name
        }
    }

    await testingCollection.add({
        documents: documents,
        ids: uuids,
        metadatas: metadatas
    })

    console.log(await testingCollection.peek({limit: 10}))
}

const filePath="types_of_testing.txt"
processLines(filePath)