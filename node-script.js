import fetch from "node-fetch";
import { spawn } from "child_process";

// Check if Ollama is running
async function isOllamaRunning() {
  try {
    const res = await fetch("http://localhost:11434");
    return res.ok;
  } catch {
    return false;
  }
}

// Start Ollama if it's not running
function startOllama() {
  const ollama = spawn("ollama", ["serve"], {
    detached: true,
    stdio: "ignore",
  });
  ollama.unref();
  console.log("✅ Ollama started in the background...");
}

// Ask a question to Llama
async function askLlama(prompt) {
  const res = await fetch("http://localhost:11434/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "llama3", // or "llama2" depending on what you pulled
      prompt,
    }),
  });

  const reader = res.body.getReader();
  let answer = "";

  // Streaming response
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = JSON.parse(new TextDecoder().decode(value));
    if (chunk.response) {
      answer += chunk.response;
    }
  }

  console.log("\n🤖 Llama says:", answer.trim());
}

(async () => {
  const running = await isOllamaRunning();
  if (!running) {
    console.log("⚠️ Ollama is not running. Starting it now...");
    startOllama();
    // wait a bit for the server to boot
    await new Promise((res) => setTimeout(res, 4000));
  } else {
    console.log("✅ Ollama is already running.");
  }

  // Ask the model something
  await askLlama("Hello Llama! How are you?");
})();
