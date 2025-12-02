```
npm init -y    
npm install --save-dev typescript
npx tsc --init
``` 

essential commands for using chromadb with typescript

```
npm install chromadb @chroma-core/default-embed
chroma run --port=9000
```

some handy commands to interact with chromadb
```
await client.reset();
await client.getCollections();
await client.listCollections({ limit: 100 });
```


- If you add a record with an ID that already exists in the collection, it will be ignored and no exception will be raised.
- Chroma also supports an upsert operation, which updates existing items, or adds them if they don't yet exist.
- by default the output from the vector retrieval is in columnar form. But i want it in row form. i can do it by `rows()` method.
- what to return i can mention inside the `include` argument.
- use `await client.reset()`

**configuration** 

```ts
embeddingFunction: new DefaultEmbeddingFunction({
    modelName: "Xenova/all-MiniLM-L6-v2"
}),
hnswConfig: { space: "cosine" }
```

```
npm install --save-dev @types/esprima
```