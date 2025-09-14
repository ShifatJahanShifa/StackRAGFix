import ollama 

""" Tool function: add two numbers"""
def addNumbers(a: int, b: int) -> int: 
    """ take two numbers and return their summation"""
    return a+b 

chatModel = 'llama3.1:8b'
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. You can do math by calling a function 'addNumbers' if needed."
    },
    {
        "role": "user",
        "content": "what is 20+10?"
    }
]
tools = [addNumbers]

response = ollama.chat(model=chatModel, messages=messages, tools=tools)

availableFunctions = {"addNumbers": addNumbers}

botsReply = response.message.content

# print('Bot (initial):', botsReply) 
if response.message.content:
    print("Bot (initial):", response.message.content)
if response.message.tool_calls:
    print("Bot (initial tool call):", response.message.tool_calls)


for tool_call in (response.message.tool_calls or []): 
    func = availableFunctions.get(tool_call.function.name)
    if func: 
        arguments = tool_call.function.arguments
        result = func(**arguments)
        messages.append({
            "role": "assistant",
            "content": f"The result is {result}"
        })
        response = ollama.chat(model=chatModel, messages=messages)
        print("Bot (final):", response.message.content)
