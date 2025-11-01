import numpy as np
import ollama

model_name = "phi4"
messages = [
    {
        'role': "user",
        # 'content': "Explain the concept of black holes in simple terms."
        'content': "Who is the president of India? STRICTLY provide the answer only"
    }
]

response = ollama.chat(model=model_name, messages=messages)
print(response['message']['content'])

# response = ollama.chat(model=model_name, messages=messages, stream=True)
# for chunk in response:
#     print(chunk['message']['content'], end='', flush=True)
# print()