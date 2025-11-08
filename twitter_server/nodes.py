#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15

from twitter_server.generate_chain import create_generate_chain


class GraphNodes:
    def __init__(self, llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter):
        self.llm = llm
        self.retriever = retriever
        self.retrieval_grader = retrieval_grader
        self.hallucination_grader = hallucination_grader
        self.code_evaluator = code_evaluator
        self.question_rewriter = question_rewriter
        self.generate_chain = create_generate_chain(llm)

    async def retrieve(self, state):
        """
        Retrieve documents based on input question and add them to graph state.
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---Node: Starting tweet retrieval---")
        question = state["input"]
        
        # Initialize retry_count if not present
        retry_count = state.get("retry_count", 0)

        # Execute retrieval
        try:
            documents = await self.retriever.get_retriever(keywords=[question], page=1)
            print(f"Retrieved Docs: {documents}")
            return {"documents": documents, "input": question, "retry_count": retry_count}
        except RuntimeError as e:
            # Handle "no access to X" error
            print(f"Retrieval failed: {str(e)}")
            error_message = str(e)
            # Return empty documents with error information
            return {"documents": [], "input": question, "retry_count": retry_count, "error": error_message}

    def generate(self, state):
        """
        Generate answer using input question and retrieved documents, and add generation to graph state.
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        print("---Node: Generating response---")

        question = state["input"]
        documents = state["documents"]
        retry_count = state.get("retry_count", 0)
        error_message = state.get("error", None)

        # Handle error from retrieval (no access to X)
        if error_message:
            print(f"---Error detected: {error_message}---")
            generation = f"I apologize, but I couldn't access X (Twitter) to retrieve information. Error: {error_message}"
            return {"documents": documents, "input": question, "generation": generation, "retry_count": retry_count}

        # Handle empty documents list
        if not documents:
            print("---No documents available, generating response without context---")
            generation = "I apologize, but I couldn't retrieve any relevant information from X (Twitter) at this time. This might be due to API limitations or network issues. Please try again later or rephrase your question."
            return {"documents": documents, "input": question, "generation": generation, "retry_count": retry_count}

        # RAG-based generation
        generation = self.generate_chain.invoke({"context": documents, "input": question})
        print(f"Generated response: {generation}")
        return {"documents": documents, "input": question, "generation": generation, "retry_count": retry_count}

    def grade_documents(self, state):
        """
        Rephrase input question to improve clarity and relevance, and update graph state with transformed question.
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """
        print("---Node: Checking if retrieved tweets are relevant to the question---")
        question = state["input"]
        documents = state["documents"]
        retry_count = state.get("retry_count", 0)

        # Handle empty documents list
        if not documents:
            print("---No documents to grade, returning empty list---")
            return {"documents": [], "input": question, "retry_count": retry_count}

        filtered_docs = []

        for d in documents:
            score = self.retrieval_grader.invoke({"input": question, "document": d.page_content})
            grade = score["score"]
            if grade == "yes":
                print("---Evaluation result: Retrieved tweet is relevant to question---")
                filtered_docs.append(d)
            else:
                print("---Evaluation result: Retrieved tweet is not relevant to question---")
                continue

        return {"documents": filtered_docs, "input": question, "retry_count": retry_count}

    def transform_query(self, state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """
        print("---Node: Rewriting user input question---")

        question = state["input"]
        documents = state["documents"]
        retry_count = state.get("retry_count", 0) + 1
        
        print(f"---Retry attempt: {retry_count}/3---")

        # Question rewriting
        better_question = self.question_rewriter.invoke({"input": question})
        print(f"Rewritten question: {better_question}")
        return {"documents": documents, "input": better_question, "retry_count": retry_count}
