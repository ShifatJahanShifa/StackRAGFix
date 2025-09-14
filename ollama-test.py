# import requests
# import subprocess
# import time
# import json

# # Check if Ollama is running
# def is_ollama_running():
#     try:
#         res = requests.get("http://localhost:11434")
#         return res.status_code == 200
#     except requests.exceptions.ConnectionError:
#         return False

# # Start Ollama if it's not running
# def start_ollama():
#     subprocess.Popen(
#         ["ollama", "serve"],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#         stdin=subprocess.DEVNULL,
#         close_fds=True
#     )
#     print("✅ Ollama started in the background...")

# # Ask a question to Llama (streaming version)
# def ask_llama(prompt: str):
#     with requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "llama3",  # or "llama2"
#             "prompt": prompt,
#             "stream": True
#         },
#         stream=True
#     ) as res:
#         print("\n🤖 Llama says: ", end="", flush=True)
#         for line in res.iter_lines():
#             if line:
#                 try:
#                     data = json.loads(line.decode("utf-8"))
#                     if "response" in data:
#                         print(data["response"], end="", flush=True)
#                 except json.JSONDecodeError:
#                     continue
#         print()  # newline at the end

# if __name__ == "__main__":
#     if not is_ollama_running():
#         print("⚠️ Ollama is not running. Starting it now...")
#         start_ollama()
#         time.sleep(4)  # wait for Ollama to boot
#     else:
#         print("✅ Ollama is already running.")

#     ask_llama("Hello Llama! How are you?")

import requests
import subprocess
import time

# Check if Ollama is running
def is_ollama_running():
    try:
        res = requests.get("http://localhost:11434")
        return res.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

# Start Ollama if it's not running
def start_ollama():
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        close_fds=True
    )
    print("✅ Ollama started in the background...")

# Ask a question to Llama (non-streaming version)
def ask_llama(prompt: str):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",   # or "llama2"
            "prompt": prompt
        }
    )
    # The API returns JSON lines, we want the "response" field
    answer = ""
    for line in res.text.splitlines():
        if line.strip():
            data = res.json() if line == res.text else eval(line)
            if "response" in data:
                answer += data["response"]

    print("\n🤖 Llama says:", answer.strip())

if __name__ == "__main__":
    if not is_ollama_running():
        print("⚠️ Ollama is not running. Starting it now...")
        start_ollama()
        time.sleep(4)  # wait a bit for Ollama server to boot
    else:
        print("✅ Ollama is already running.")

    ask_llama("Hello Llama! How are you?")
