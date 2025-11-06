#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-16

# https://bigmodel.cn/

import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Fill in your own APIKey in the .env file
client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))
response = client.chat.completions.create(
    model="glm-4-plus",  # Fill in the model code to call
    messages=[
        {"role": "system", "content": "You are a helpful assistant, your task is to provide professional, accurate, and insightful advice to users."},
        {"role": "user", "content": "A farmer needs to transport a wolf, a sheep, and cabbage across a river, but can only take one item at a time. The wolf and sheep cannot be left alone together, nor can the sheep and cabbage. How should the farmer cross the river?"}
    ],
)
print(response.choices[0].message)