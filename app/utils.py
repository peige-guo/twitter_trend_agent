#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15

from langchain_openai import ChatOpenAI
from twitter_server.document_loader import DocumentLoader
from twitter_server.edges import EdgeGraph
from twitter_server.generate_chain import create_generate_chain
from twitter_server.graph import GraphState
from twitter_server.grader import GraderUtils
from twitter_server.nodes import GraphNodes

from langgraph.graph import END, StateGraph


def create_parser_components(api_key: str, model: str):
    """
    Create and initialize parser components and grader instances.

    Args:
    api_key (str): API key for accessing DeepSeek services.

    Returns:
    dict: Dictionary containing all created component instances.
    """

    # Create retriever instance for document retrieval
    retriever = DocumentLoader()

    # Create LLM model instance, configured to use DeepSeek model with specified temperature parameter
    print(f"Initializing LLM with model: {model}")
    print(f"Base URL: https://api.deepseek.com")
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",  # Add /v1 endpoint
        model=model,
        temperature=0
    )

    # Create generation chain for language model-based generation tasks
    generate_chain = create_generate_chain(llm)

    # Initialize grader instance for creating and managing various grading tools
    grader = GraderUtils(llm)

    # Create grader for evaluating relevance of retrieved documents to user questions
    retrieval_grader = grader.create_retrieval_grader()

    # Create grader for evaluating whether model's answers contain hallucinations
    hallucination_grader = grader.create_hallucination_grader()

    # Create code evaluator for assessing correctness of code execution results
    code_evaluator = grader.create_code_evaluator()

    # Create question rewriter to optimize user questions for better model understanding and answering
    question_rewriter = grader.create_question_rewriter()

    # Return dictionary containing all components for use in other parts of the code
    return {
        "llm": llm,
        "retriever": retriever,
        "generate_chain": generate_chain,
        "retrieval_grader": retrieval_grader,
        "hallucination_grader": hallucination_grader,
        "code_evaluator": code_evaluator,
        "question_rewriter": question_rewriter
    }


def create_workflow(api_key: str, model: str):
    """
    Create and initialize workflow along with its constituent nodes and edges.

    Returns:
    StateGraph: Fully initialized and compiled workflow object.
    """

    # Call function and directly destructure dictionary to get all instances
    (llm, retriever, generate_chain,
     retrieval_grader, hallucination_grader,
     code_evaluator, question_rewriter) = create_parser_components(api_key, model).values()

    # Initialize graph structure
    workflow = StateGraph(GraphState)

    # Create graph nodes instance
    graph_nodes = GraphNodes(llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter)

    # Create edge nodes instance
    edge_graph = EdgeGraph(hallucination_grader, code_evaluator)

    # Define nodes
    workflow.add_node("retrieve", graph_nodes.retrieve)  # retrieve documents
    workflow.add_node("grade_documents", graph_nodes.grade_documents)  # grade documents
    workflow.add_node("generate", graph_nodes.generate)  # generate answers
    workflow.add_node("transform_query", graph_nodes.transform_query)  # transform query

    # Create graph
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        edge_graph.decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        }
    )
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_conditional_edges(
        "generate",
        edge_graph.grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": END,
            "not useful": "transform_query",
        }
    )

    # Compile graph
    chain = workflow.compile()
    return chain


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    create_workflow(os.getenv('DEEPSEEK_API_KEY'),
                    os.getenv('model', 'deepseek-chat'),
                    )
