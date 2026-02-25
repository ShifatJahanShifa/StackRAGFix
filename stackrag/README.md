# StackRAG — Intelligent Code Assistant for VS Code

StackRAG is a **Retrieval-Augmented Generation (RAG)** powered VS Code extension that helps developers understand, debug, and improve their code using real-world knowledge from Stack Overflow and their own codebase.

It combines:

* 🔍 Codebase-aware retrieval
* 🧠 Stack Overflow knowledge
* 🤖 LLM-powered reasoning
* ⚡ Fast hybrid search

---

## ✨ Features

### 🧩 Codebase Understanding

* Automatically indexes your workspace
* Language-aware chunking for Python and JavaScript
* Semantic code search across your project

### 🐛 Intelligent Bug Fixing

* Detects issues in your code
* Suggests fixes with explanations
* Uses real Stack Overflow solutions as evidence

### ♻️ Smart Refactoring

* Improves code quality and structure
* Applies best-practice patterns
* Maintains original functionality

### 🔎 Hybrid Retrieval

* BM25 + Vector search ensemble
* Context-aware ranking
* High-quality relevant results

---

## 🛠️ Supported Languages

* ✅ Python
* ✅ JavaScript

(More languages coming soon)

---

## 📦 Installation

1. Install from the VS Code Marketplace
2. Reload VS Code
3. Configure your API key (see below)

---

## 🔑 Required Setup

StackRAG requires your own **Mistral API key**.

### Step 1 — Open VS Code Settings

Search for:

```
StackRAG: Mistral Api Key
StackRAG: Qdrant Cluster Endpoint
StackRAG: Qdrant Api Key
```

### Step 2 — Paste your key

Or add to `settings.json`:

```json
{
  "stackrag.mistralApiKey": "your-api-key-here",
  "stackrag.qdrantClusterEndpoint": "provide the endpoint",
  "stackrag.qdrantApiKey": "your-qdrant-api-key"
}
```

⚠️ Your key is stored locally and never uploaded.

---

## 🚀 How to Use

### 1️⃣ Index Your Workspace

* Open Command Palette
* Run:

```
StackRAG: Index Workspace
```

This builds the semantic code index.

---

### 2️⃣ Ask Questions

Use the StackRAG panel to:

* Explain code
* Fix bugs
* Refactor functions
* Search relevant patterns

---

### 3️⃣ Bug Fixing

Provide:

* Bug description
* Code snippet
* Optional related files

StackRAG will generate:

* ✅ Fixed code
* ✅ Explanation
* ✅ Supporting evidence

---

## 🧠 How It Works (High Level)

StackRAG uses a multi-stage RAG pipeline:

1. Workspace code chunking
2. Stack Overflow knowledge retrieval
3. Hybrid search (BM25 + vector)
4. LLM reasoning with context

This produces grounded, high-quality answers.

---

## 🔒 Privacy & Security

* Your code stays local
* No automatic uploads
* API key stored in VS Code settings
* You control all indexing

---

## 🐞 Known Limitations

* Large repositories may take time to index
* Currently optimized for Python and JavaScript
* Requires user-provided API key

---

## 🗺️ Roadmap

* More language support
* Smarter repository summarization
* Improved ranking
* Streaming responses
* UI enhancements

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## ⭐ Support

If you find StackRAG helpful, consider giving it a star on GitHub!

---

**Built to make code understanding faster and smarter.**
