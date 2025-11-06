#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15

import os
import sys

# Add parent directory to Python path to enable imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from pydantic import BaseModel
from app.utils import create_workflow

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Initialize workflow for graph nodes
chain = create_workflow(os.getenv('DEEPSEEK_API_KEY'),
                        os.getenv('model', 'deepseek-chat'),
                        )


class Input(BaseModel):
    input: str


class Output(BaseModel):
    output: dict


app = FastAPI(
    title="XAgent Server",
    version="1.0",
    description="An API named twitter_server designed specifically for real-time retrieval of live data from X (Twitter)."
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Add routes
add_routes(
    app,
    chain.with_types(input_type=Input, output_type=Output),
    path="/xagent_chat",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
