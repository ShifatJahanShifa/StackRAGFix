Perfect 👍 Let’s go through the **official Ollama Python library function signatures** with parameters + return shapes.

I’ll cover **all the main APIs** you’ll actually use (`generate`, `chat`, `embed`, model management, etc.).

---

# 🔹 Ollama Python API — Function Signatures

### 1. `ollama.generate()`

```python
ollama.generate(
    model: str,
    prompt: str,
    system: str | None = None,
    template: str | None = None,
    context: list[int] | None = None,
    images: list[bytes] | None = None,
    format: dict | str | None = None,
    options: dict | None = None,
    keep_alive: str | int | None = None,
    stream: bool = False,
) -> dict | Generator[dict, None, None]
```

* **Returns**:

  * If `stream=False`: a single `dict` with keys like `response`, `context`, `done_reason`, timings, etc.
  * If `stream=True`: a generator yielding partial dicts with `response` chunks.

---

### 2. `ollama.chat()`

```python
ollama.chat(
    model: str,
    messages: list[dict],   # [{"role": "user"|"assistant"|"system", "content": str, "images": [...]}]
    tools: list[dict] | None = None,
    format: dict | str | None = None,
    options: dict | None = None,
    keep_alive: str | int | None = None,
    stream: bool = False,
) -> dict | Generator[dict, None, None]
```

* **Returns**:

  * If `stream=False`: a dict with a final `message` (assistant reply).
  * If `stream=True`: a generator yielding partial responses.

---

### 3. `ollama.embed()`

```python
ollama.embed(
    model: str,
    input: str | list[str],
    options: dict | None = None,
    keep_alive: str | int | None = None,
) -> dict
```

* **Returns**:

```python
{
  "model": "string",
  "embeddings": [[float, ...], ...],  # list of vectors
}
```

---

### 4. `ollama.list()`

```python
ollama.list() -> dict
```

* **Returns**:

```python
{
  "models": [
    {
      "name": "mistral:latest",
      "size": 123456789,
      "digest": "sha256:...",
      "details": {...},
    },
    ...
  ]
}
```

---

### 5. `ollama.show()`

```python
ollama.show(model: str) -> dict
```

* Shows metadata of a model (format, family, quantization, size, etc.)

---

### 6. `ollama.ps()`

```python
ollama.ps() -> dict
```

* Lists **running / loaded models** in memory.
* Example response:

```python
{
  "models": [
    {
      "name": "llama3.2",
      "size": 456789,
      "expires_at": "2025-09-04T12:34:56Z"
    }
  ]
}
```

---

### 7. `ollama.pull()`

```python
ollama.pull(model: str, stream: bool = False) -> dict | Generator[dict, None, None]
```

* Downloads a model.
* If `stream=True`, yields progress events.

---

### 8. `ollama.push()`

```python
ollama.push(model: str, stream: bool = False, insecure: bool = False) -> dict | Generator[dict, None, None]
```

* Uploads a model to a registry (if you’re authenticated).

---

### 9. `ollama.create()`

```python
ollama.create(
    model: str,
    modelfile: str,
    stream: bool = False,
) -> dict | Generator[dict, None, None]
```

* Creates a model from a `Modelfile` definition.

---

### 10. `ollama.copy()`

```python
ollama.copy(source: str, destination: str) -> dict
```

* Copies a model to a new name.

---

### 11. `ollama.delete()`

```python
ollama.delete(model: str) -> dict
```

* Deletes a local model.

---

✅ With these signatures you can:

* Stream completions like OpenAI.
* Manage models (list, show, ps, pull, push, create, copy, delete).
* Use embeddings for your RAG system.
* Add tools for function-calling style workflows.

---

Do you want me to also prepare a **ready-to-use Python client wrapper** (like an `OllamaClient` class) so you can call `client.chat()`, `client.generate()`, etc. instead of raw functions? That’ll make your RAG project cleaner.
