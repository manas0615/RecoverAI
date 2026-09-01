import re

with open('recoverai/llm_gateway/config.py', 'r') as f:
    text = f.read()

text = text.replace('groq/compound', 'qwen/qwen3.6-27b')

with open('recoverai/llm_gateway/config.py', 'w') as f:
    f.write(text)

