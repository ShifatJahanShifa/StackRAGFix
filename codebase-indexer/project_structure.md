codebase-indexer/
├── src/
│   ├── extension.ts          # Main entry (VSCode extension)
│   ├── indexer/
│   │   ├── fileScanner.ts    # Scans workspace for files
│   │   ├── embedder.ts       # Creates embeddings (via API or local model)
│   │   ├── vectorStore.ts    # Stores & retrieves embeddings
│   │   └── watcher.ts        # Watches file changes
│   └── utils/
│       └── helpers.ts
├── package.json
├── tsconfig.json
└── README.md
