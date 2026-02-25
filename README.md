# StackRAGFix
A tool for code repair with RAG system based on Stack Overflow.

## SYSTEM ARCHITECTURE:
The StackRAGFix project uses a Hybrid RAG (Retrieval-Augmented Generation) architecture:

1. INGESTION LAYER (kb/):
   - Fetches code from workspace or Stack Overflow
   - Chunks code into semantic units using language-specific chunkers
   - Generates embeddings for each chunk
   - Stores in Chroma vector database

2. INDEXING LAYER (stackrag/indexing/):
   - Manages code ingestion from VS Code workspace
   - Coordinates chunking and embedding processes
   - Maintains vector store indexes
   - Provides query interface for retrieval

3. RETRIEVAL LAYER (backend/src/):
   - Implements hybrid search (semantic + BM25)
   - Custom ensemble retriever combines multiple search methods
   - Performs keyword extraction from queries
   - Returns ranked and reranked results

4. GENERATION LAYER (backend/src/):
   - Takes retrieved context + user query
   - Uses LLM with RAG prompts
   - Generates responses, bug fixes, refactorings, summaries
   - Maintains conversation context for multi-turn chat

5. PRESENTATION LAYER (stackrag/view/):
   - VS Code webview for chat interface
   - Real-time message display
   - Code suggestion highlighting
   - Integration with VS Code editor


## DATA FLOW 

1: USER ASKS A QUESTION
Flow:
1. User types query in chatWebView.html
2. chatWebView.ts sends message to extension.ts
3. extension.ts forwards to backend Flask app
4. backend/src/chat.py process_chat_message() is called
5. keyword_extractor.py extracts keywords from query
6. custom_ensemble_retriever.py performs hybrid search
   - semantic_search() on vector store via vector_store_retriever.py
   - bm25_search() on indexed text via bm25.py
   - Results are merged with weights from weights.py
7. Retrieved context is formatted by prompts/chat_prompt.py
8. models/model_instances.py calls LLM (e.g., Claude, GPT)
9. Response flows back through extension to chatWebView.ts
10. User sees response with cited code snippets

2: USER ASKS FOR BUG FIX
Flow:
1. User submits code + bug description in chat
2. backend/src/bug_fixing.py analyze_bug() is called
3. vector_store_retriever.py retrieves similar code patterns
4. prompts/bug_fixing_prompt.py formats context
5. LLM analyzes code for bugs
6. generate_fix() creates fix suggestions
7. explain_fix() creates explanation
8. Results returned to user with before/after code

3: CODEBASE INDEXING
Flow:
1. Extension activated in VS Code
2. indexing/indexService.ts buildIndex() starts
3. indexing/codeIngestion.ts scans workspace
4. Files filtered and read
5. jsChunker.ts or pyChunker.ts processes code
6. indexing/vector_store.ts generates embeddings
7. Chroma vector database stores embeddings
8. kb/bm25.py builds BM25 index for keyword search
9. Index ready for queries

## KEY TECHNOLOGIES

FRONTEND:
- Visual Studio Code Extension API
- TypeScript
- HTML/CSS for webview UI
- Message passing protocol

BACKEND:
- Python 3.x
- Fast API for REST API
- LangChain for LLM integration
- Chroma for vector storage
- BM25 for keyword search

LLM PROVIDERS:
- Mistral Model
- Configurable in constants/models.py

KNOWLEDGE BASE:
- Stack Overflow data
- Local codebase
- Multiple language support (JS, Python, etc.)


## FILE ORGANIZATION SUMMARY

STACKRAG/ (10 files):
├── extension.ts (Main extension entry)
├── indexing/ (5 files)
│   ├── codeIngestion.ts
│   ├── codeQuery.ts
│   ├── indexService.ts
│   ├── jsChunker.ts
│   ├── pyChunker.ts
│   └── vector_store.ts
├── test/
│   └── extension.test.ts
└── view/ (2 files)
    ├── chatWebView.ts
    └── webView.html

BACKEND/ (35+ files):
├── app.py (Flask app)
├── constants/ (6 files)
│   ├── api.py
│   ├── collections.py
│   ├── file_paths.py
│   ├── models.py
│   ├── temperatures.py
│   └── weights.py
├── dtos/ (4 files)
│   ├── bug_fixing.py
│   ├── chat.py
│   ├── code_refactoring.py
│   └── codebase_summary.py
├── models/ (2 files)
│   ├── model_instances.py
│   └── models.py
├── prompts/ (5 files)
│   ├── bug_fixing_prompt.py
│   ├── chat_prompt.py
│   ├── code_refactoring_prompt.py
│   ├── codebase_summary_prompt.py
│   └── keyword_extractor_prompt.py
├── src/ (6 files)
│   ├── bug_fixing.py
│   ├── chat.py
│   ├── code_refactoring.py
│   ├── codebase_summary.py
│   ├── custom_ensemble_retriever.py
│   ├── keyword_extractor.py
│   └── vector_store_retriever.py
└── utils/ (3 files)
    ├── keyword_cleaner.py
    ├── logger.py
    └── pickle_loader.py

KB/ (10+ files):
├── bm25.py
├── ingestion.js
├── so_posts_fetcher.py
├── constants/ (6 files)
│   ├── collections.py
│   ├── files.py
│   ├── sites.py
│   ├── tags.py
│   ├── urls.py
│   └── vector_store.js
├── chroma/ (Vector store data)
└── chroma_store/ (Vector store data)
