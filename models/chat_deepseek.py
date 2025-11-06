#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-02

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# DeepSeek API Documentation: https://platform.deepseek.com/api-docs/
# DeepSeek uses OpenAI-compatible API
from openai import OpenAI

# Fill in your own APIKey in the .env file
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

completion = client.chat.completions.create(
    model="deepseek-chat",  # or "deepseek-coder" for coding tasks
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(completion.choices[0].message.content)

