import ollama

# get the client
client = ollama.Client()

model = "llama3:8b"
prompt = "what is python?"

response = client.generate(model=model, prompt=prompt)

print("Generating response...")
print(response.response)
