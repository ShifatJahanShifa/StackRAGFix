Here are the **current spec details** of the Ollama REST API (as of latest public docs) — request/response JSON shapes, endpoints, parameters. Use this as a reference for your coding. Some fields optional.

---

## 🔍 Ollama REST API Spec — Endpoints & JSON Shapes

Source: Ollama docs, KodeKloud notes, etc. ([Ollama][1])

---

### 1. `POST /api/generate`

**Request JSON**

```json
{
  "model": "string",           // required, e.g. "llama3.2"
  "prompt": "string",          // required, text prompt
  "suffix": "string",          // optional, appended after response
  "system": "string",          // optional, system message override
  "template": "string",        // optional, prompt template override
  "context": [int, ...],       // optional, previous context (token IDs) for memory
  "stream": boolean,           // optional, default true (if true, returns streaming chunks)
  "raw": boolean,              // optional, no formatting applied
  "format": {                  // optional, JSON schema or format object
    // schema object, e.g.
    "type": "object",
    "properties": {
      "title": { "type": "string" },
      "theme": { "type": "string" },
      "lines": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "required": ["title", "theme", "lines"]
  },
  "images": [                  // optional, for multimodal models
    {
      "data": "base64-string",   // or other image-encoding format
      "mime": "string"
    }
  ],
  "options": {                 // optional, model-specific params
    "temperature": number,
    "stop": [ "string", ... ],
    // etc
  },
  "keep_alive": "duration"     // optional, how long model stays loaded, e.g. "5m"
}
```

**Response JSON**

If `stream: false`:

```json
{
  "model": "string",
  "created_at": "ISO8601 timestamp",
  "response": "string",         // full generated text
  "done": boolean,
  "done_reason": "string",      // e.g. "stop", "length", etc
  "context": [int, ...],         // token IDs
  "total_duration": integer,     // in nanoseconds
  "load_duration": integer,      // cost to load model
  "prompt_eval_count": integer,
  "prompt_eval_duration": integer,
  "eval_count": integer,
  "eval_duration": integer
}
```

If `stream: true`:

* A sequence of JSON objects are sent. Each chunk might have:

```json
{
  "model": "string",
  "response": "string",         // partial text
  "done": boolean,
  // later, final chunk has additional metrics:
  "done_reason": "string",
  "context": [int, ...],
  "total_duration": integer,
  "load_duration": integer,
  "prompt_eval_count": integer,
  "prompt_eval_duration": integer,
  "eval_count": integer,
  "eval_duration": integer
}
```

---

### 2. `POST /api/chat`

Used for multi-turn conversations.

**Request JSON**

```json
{
  "model": "string",
  "messages": [
    {
      "role": "user" | "assistant" | "system" | "tool",
      "content": "string",
      "images": [  // optional
        {
          "data": "base64-string",
          "mime": "string"
        }
      ]
    },
    // ... more message objects
  ],
  "stream": boolean,             // optional
  "format": { ... }              // optional, JSON schema
  "options": { ... }             // optional, model params
  "keep_alive": "duration"       // optional
}
```

**Response JSON**

If `stream: false`:

```json
{
  "model": "string",
  "created_at": "ISO8601 timestamp",
  "message": {
    "role": "assistant",
    "content": "string",
    "images": null | [ ... ]    // only if provided/generated
  },
  "done": boolean,
  "done_reason": "string",       // e.g. "stop"
  "total_duration": integer,
  "load_duration": integer,
  "prompt_eval_count": integer,
  "prompt_eval_duration": integer,
  "eval_count": integer,
  "eval_duration": integer
}
```

If `stream: true`:

* Partial JSON objects similar to generate streaming: initial ones with partial content, final one with metrics etc. ([KodeKloud Notes][2])

---

### 3. `POST /api/embed` (also alias `embeddings`)

Generate embedding vectors.

**Request JSON**

```json
{
  "model": "string",
  "input": "string" | ["string", ...],   // single or list of inputs
  "options": { ... }                     // optional
  "keep_alive": "duration"               // optional
}
```

**Response JSON**

```json
{
  "model": "string",
  "embeddings": [
    [number, number, ...],   // vector for each input
    // more vectors if multiple inputs
  ],
  "total_duration": integer,
  "load_duration": integer,
  "prompt_eval_count": integer
}
```

---

### 4. Model Management Endpoints

| Endpoint      | Method                                | Request / Response JSON                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/api/ps`     | GET                                   | **Response**: list of loaded/running models. <br>Example: <br>`json { "models": [ { "name": "mistral:latest", "model": "mistral:latest", "size": integer, "digest": "string", "details": { "parent_model":"", "format":"gguf", "family":"llama", "families":[ "llama" ], "parameter_size":"7.2B", "quantization_level":"Q4_0" }, "expires_at": "timestamp", "size_vram": integer } , ... ] }` ([Postman][3]) |
| `/api/show`   | GET (likely with query param “model”) | **Response**: metadata for specified model — size, format, etc.                                                                                                                                                                                                                                                                                                                                              |
| `/api/copy`   | POST                                  | **Request**: `{ "source": "modelName", "destination": "newModelName" }` <br>**Response**: success JSON, maybe model info. ([KodeKloud Notes][4])                                                                                                                                                                                                                                                             |
| `/api/delete` | DELETE                                | **Request**: `{ "model": "modelName" }` <br>**Response**: status or confirmation.                                                                                                                                                                                                                                                                                                                            |
| `/api/pull`   | POST                                  | **Request**: `{ "model": "modelName", "stream": boolean (opt) }` <br>**Response**: stream status messages or final success. ([KodeKloud Notes][2])                                                                                                                                                                                                                                                           |
| `/api/push`   | POST                                  | **Request**: `{ "model": "namespace/model:tag", "stream": boolean (opt), "insecure": boolean (opt) }` <br>**Response**: statuses over stream or final JSON. ([Ollama][1])                                                                                                                                                                                                                                    |

---

## ⚠️ Notes & Tips

* Durations are in **nanoseconds**. ([Ollama][1])
* The `stream` field controls whether you get streaming partial output or one-shot.
* The `format` parameter allows you to enforce JSON schema formatting of response — good for structured output.
* The `keep_alive` parameter helps manage memory: how long a model is kept loaded.
* If using multimodal models, `images` field (base64) may be included. ([Ollama][1])

---

If you like, I can serialize this into an **OpenAPI Spec file (YAML/JSON)** so you can import into tools & generate clients easily.

[1]: https://ollama.readthedocs.io/en/api/?utm_source=chatgpt.com "API Reference - Ollama English Documentation"
[2]: https://notes.kodekloud.com/docs/Running-Local-LLMs-With-Ollama/Building-AI-Applications/Ollama-REST-API-Endpoints?utm_source=chatgpt.com "Ollama REST API Endpoints - KodeKloud Notes"
[3]: https://www.postman.com/postman-student-programs/documentation/21521806-f48dc31a-a9f1-4dad-9082-fd07f5cd2fda?entity=request-21521806-3f80ff0f-96ce-4367-96ed-6bfc60f8a7cf&utm_source=chatgpt.com "Ollama REST API | Documentation | Postman API Network"
[4]: https://notes.kodekloud.com/docs/Running-Local-LLMs-With-Ollama/Building-AI-Applications/Demo-Using-Ollama-API-and-Interacting-With-It?utm_source=chatgpt.com "Demo Using Ollama API and Interacting With It - KodeKloud Notes"
