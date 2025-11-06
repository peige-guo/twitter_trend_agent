#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-02

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# DeepSeek API Documentation: https://platform.deepseek.com/api-docs/
# DeepSeek uses OpenAI-compatible API with custom base_url

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat",  # or "deepseek-coder" for coding tasks
)

messages = [
    (
        "system", "You are a helpful assistant that translates English to Chinese. Translate the user sentence.",
    ),
    (
        "human", "I love programming."
    ),
]

ai_msg = llm.invoke(messages)
print(ai_msg.content)

