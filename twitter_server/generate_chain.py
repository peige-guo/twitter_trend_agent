#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15

import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def create_generate_chain(llm):
    """
    Creates a generate chain for answering X (Twitter) related questions.

    Args:
        llm (LLM): The language model to use for generating responses.

    Returns:
        A callable function that takes a context and a question as input and returns a string response.
    """
    generate_template = """
    You are an AI personal assistant named FuFan. Users will pose questions related to X (Twitter) data, which are presented in the parts enclosed by <context></context> tags.
    
    Use this information to formulate your answers.
    
    When a user's question requires fetching data by scraping X (Twitter), you may proceed accordingly.
    If you cannot find an answer, please respond honestly that you do not know. Do not attempt to fabricate an answer.  
    If the question is unrelated to the context, politely respond that you can only answer questions related to the context provided.
    
    For questions involving data analysis, please write the code in Python and provide a detailed analysis of the results to offer as comprehensive an answer as possible.
    
    <context>
    {context}
    </context>
    
    <question>
    {input}
    </question>
    """

    generate_prompt = PromptTemplate(template=generate_template, input_variables=["context", "input"])

    # Without StrOutputParser(), output might look like this:
    # {
    #     "content": "This is the response from the LLM.",
    #     "metadata": {
    #         "confidence": 0.8,
    #         "response_time": 0.5
    #     }
    # }

    # With StrOutputParser(), it looks like this:
    # This is the response from the LLM.

    # Create the generate chain
    generate_chain = generate_prompt | llm | StrOutputParser()

    return generate_chain


if __name__ == '__main__':
    # Using DeepSeek API (OpenAI-compatible)
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'),
                     base_url="https://api.deepseek.com",
                     model=os.getenv('model', 'deepseek-chat'),
                     )

    # Create a generation chain
    generate_chain = create_generate_chain(llm)
    final_answer = generate_chain.invoke({
        "context": "Here are the popular tweets I found: AI trends are fascinating! New developments in machine learning. Check out this research paper about ChatGPT applications.",
        "input": "Please help me summarize the information from popular tweets"
    })
    print(final_answer)
