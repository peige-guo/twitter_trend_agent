from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
        retry_count: number of query transformation retries
    """

    input: str
    generation: str
    documents: str
    retry_count: int