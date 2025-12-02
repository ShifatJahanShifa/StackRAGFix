import { ChromaClient } from "chromadb";
import { getCollection } from "./chromaCollection.js";
const client = new ChromaClient({
    host: "localhost",
    port: 9000
});
const testingCollection = await getCollection("testing1");
const results = await testingCollection.
    // peek({limit: 30})
    query({
    queryTexts: ["what is the regression testing?"],
    nResults: 2
});
console.log(results);
console.log(testingCollection.name);
console.log(testingCollection.configuration.hnsw);
// to see the list of collections 
console.log(await client.listCollections({ limit: 10 }));
// to rename the collection
// await testingCollection.modify({
//     name: "testing"
// })
// to delete a collection
// await client.deleteCollection({ name: "testing"})
// convenience methods. count and peek
console.log(await testingCollection.count());
// console.log(await testingCollection.peek({limit: 25})); 
// let records=await testingCollection.get({limit: 25, include:['embeddings']})
// console.log(records.rows())
// update collection
// await testingCollection.upsert({
//     ids: ["id1"],
//     metadatas: [{"chapter": 3, "verse": 16}],
//     documents: ["doc1..."]
// })
// delete collection
// await testingCollection.delete({
//     where: {"chapter": 3}
// })
// by using query
// console.log(await testingCollection.query({
//     queryTexts: ['integration testing'],
//     ids: ['8c7126fa-28e7-4fe9-9e0d-49ab4fe4c816']
// }))
// by using get..., limit, offset, wheredocument...
// const result = await testingCollection.get({
//     whereDocument: {'$contains': 'correctly'}
// })
// console.log('ss', result)
// query by filtering metadata
let outputs = await testingCollection.get({
    // queryTexts: ['testing'],
    whereDocument: { $contains: "correctly" }
});
console.log(outputs);
