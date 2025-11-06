#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class GraderUtils:
    def __init__(self, model):
        self.model = model

    def create_retrieval_grader(self):
        """
        Creates a retrieval grader that assesses the relevance of a retrieved document to a user question.

        Returns:
            A callable function that takes a document and a question as input and returns a JSON object with a binary score indicating whether the document is relevant to the question.
        """

        # Special tokens are used to specify the start and end of different parts and clarify different types of text blocks.
        # These tokens help the large model better understand and distinguish different parts of input data, enabling more precise execution of specific tasks.
        # You are a grader evaluating the relevance of retrieved documents to user questions. If the document contains keywords related to the user question, rate it as relevant. This does not need to be a very strict test. The goal is to filter out erroneous retrieval results.
        grade_prompt = PromptTemplate(
            template="""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>

            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {input} \n
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            """,
            input_variables=["document", "input"],
        )

        # Create a retrieval chain
        retriever_grader = grade_prompt | self.model | JsonOutputParser()

        return retriever_grader

    # You are a grader responsible for evaluating whether an answer is based on/supported by a set of facts. Give a binary score of "yes" or "no" to indicate whether the answer is based on/supported by facts. Provide a JSON with a single key "score" without preamble or explanation.
    def create_hallucination_grader(self):
        """
        Creates a hallucination grader that assesses whether an answer is grounded in/supported by a set of facts.

        Returns:
            A callable function that takes a generation (answer) and a list of documents (facts) as input and returns a JSON object with a binary score indicating whether the answer is grounded in/supported by the facts.
        """
        hallucination_prompt = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
            You are a grader assessing whether an answer is grounded in / supported by a set of facts. Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Here are the facts:
            \n ------- \n
            {documents}
            \n ------- \n
            Here is the answer: {generation}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "documents"],
        )

        hallucination_grader = hallucination_prompt | self.model | JsonOutputParser()

        return hallucination_grader

    def create_code_evaluator(self):
        """
        Creates a code evaluator that assesses whether the generated code is correct and relevant to the given question.

        Returns:
            A callable function that takes a generation (code), a question, and a list of documents as input and returns a JSON object with a binary score and feedback.
        """
        eval_template = PromptTemplate(
            template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a code evaluator assessing whether the generated code is correct and relevant to the given question.
            Provide a JSON response with the following keys:

            'score': A binary score 'yes' or 'no' indicating whether the code is correct and relevant.
            'feedback': A brief explanation of your evaluation, including any issues or improvements needed.

            <|eot_id|><|start_header_id|>user<|end_header_id|>
            Here is the generated code:
            \n ------- \n
            {generation}
            \n ------- \n
            Here is the question: {input}
            \n ------- \n
            Here are the relevant documents: {documents}
            <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=["generation", "input", "documents"],
        )

        code_evaluator = eval_template | self.model | JsonOutputParser()

        return code_evaluator

    # You are a question rewriter that converts an input question into a better version, optimized for vector store retrieval. Look at the input and try to understand its underlying semantic intent/meaning.
    def create_question_rewriter(self):
        """
        Creates a question rewriter chain that rewrites a given question to improve its clarity and relevance.

        Returns:
            A callable function that takes a question as input and returns the rewritten question as a string.
        """
        re_write_prompt = PromptTemplate(
            template="""
            You a question re-writer that converts an input question to a better version that is optimized for vectorstore retrieval. Look at the input and try to reason about the underlying sematic intent / meaning.

            Here is the initial question: {input}

            Formulate an improved question.""",

            input_variables=["input"],
        )

        question_rewriter = re_write_prompt | self.model | StrOutputParser()

        return question_rewriter


if __name__ == '__main__':
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        model=os.getenv("model", "deepseek-chat"),
    )

    # Create an instance of the grader class
    grader = GraderUtils(llm)

    # # Create a retrieval evaluator
    # retrieval_grader = grader.create_retrieval_grader()
    #
    # # This is irrelevant
    # retrieval_grader_results = retrieval_grader.invoke({
    #     "document": "Hahaha",
    #     "input": "What are the descriptions of popular tweets about AI?"
    # })
    #
    # # This is relevant
    # # retrieval_grader_results = retrieval_grader.invoke({
    # #     "document": "Here are popular tweet descriptions I found: AI trends, machine learning developments, ChatGPT applications.",
    # #     "input": "What are the descriptions of popular tweets about AI?"
    # # })
    #
    # print(f"retrieval_grader_results: {retrieval_grader_results}")

    # # Create a hallucination detection generator
    # hallucination_grader = grader.create_hallucination_grader()
    #
    # # This is a hallucinated response
    # # hallucination_grader_results = hallucination_grader.invoke({
    # #     "documents": "Here are popular tweet descriptions: AI trends, machine learning developments.",
    # #     "generation": "Hello"
    # # })
    #
    # # This is a response based on retrieved content
    # hallucination_grader_results = hallucination_grader.invoke({
    #     "documents": "Here are popular tweet descriptions: AI trends, machine learning developments.",
    #     "generation": "For AI-related popular tweets, you can think from perspectives of trends, developments, and applications"
    # })
    #
    # print(f"hallucination_grader_results:{hallucination_grader_results}")
    #
    # # Get the code evaluator
    # code_evaluator = grader.create_code_evaluator()

    # Rewrite the input question
    question_rewriter = grader.create_question_rewriter()
    question_rewriter_results = question_rewriter.invoke({
        "input": "For AI-related tweets, how should I write a trending title description?"
    })
    print(f"question_rewriter_results: {question_rewriter_results}")
