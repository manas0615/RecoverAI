import re

with open('recoverai/llm_gateway/config.py', 'r') as f:
    text = f.read()

text = text.replace('llama-3.3-70b-versatile', 'groq/compound')

with open('recoverai/llm_gateway/config.py', 'w') as f:
    f.write(text)

