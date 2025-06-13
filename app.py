import ollama

response = ollama.chat(
    model='qwen3:0.6b',  
    messages=[
        {'role': 'user', 'content': 'Hello, how are you?'}
    ]
)
print(response['message']['content'])