import json

import requests

# base url
url = "http://localhost:11434/api/chat"

# confiure json payload
payload = {
    "model": "llama3:8b",
    "messages": [{"role": "user", "content": "what is python?"}],
    "stream": True,
}

response = requests.post(url=url, json=payload)

if response.status_code == 200:
    print("streaming response from ollama...")
    for line in response.iter_lines(decode_unicode=True):
        try:
            # decode the line as json
            json_data = json.loads(line)
            if "message" in json_data and "content" in json_data["message"]:
                print(json_data["message"]["content"], end="")
        except json.JSONDecodeError:
            print(f"Failed to parse line: {line}")

    print()
else:
    print(f"Error: {response.status_code}")
    print(response.text)
