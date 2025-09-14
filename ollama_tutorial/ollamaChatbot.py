# chatbot
import ollama 

modelName = 'llama3:8b'
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "hello"
    }
]

response = ollama.chat(model=modelName, messages=messages)
print('Bot:', response['message']['content'])

while True:
    userInput = input('You: ')
    if not userInput:
        break
    messages.append({
        "role": "user",
        "content": userInput
    })
    response = ollama.chat(model=modelName, messages=messages)
    answer = response['message']['content']
    print('Bot:', answer)
    messages.append({
        "role": "assistant",
        "content": answer
    })