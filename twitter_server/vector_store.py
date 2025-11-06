#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15


from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from twitter_server.document_loader import DocumentLoader


def get_local_store(store_path: str) -> FAISS:
    """
    Loads a locally stored FAISS vector store.

    Args:
        store_path (str): The path where the FAISS vector store is stored locally.

    Returns:
        FAISS: The loaded FAISS vector store.
    """
    # Load Embedding model (must match the model used to create the store)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # Load Faiss database directly from local storage
    store = FAISS.load_local(store_path, embedding_model, allow_dangerous_deserialization=True)

    return store


async def create_vector_store(docs, store_path: Optional[str] = None) -> FAISS:
    """
    Creates a FAISS vector store from a list of documents.

    Args:
        docs (List[Document]): A list of Document objects containing the content to be stored.
        store_path (Optional[str]): The path to store the vector store locally. If None, the vector store will not be stored.

    Returns:
        FAISS: The FAISS vector store containing the documents.
    """
    # Build text splitter (tweets are shorter, use smaller chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    print("docs: ", docs)
    texts = text_splitter.split_documents(docs)

    # Embedding object - using HuggingFace for free, local embeddings
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # Create the FAISS vector store
    store = FAISS.from_documents(texts, embedding_model)

    # Save the vector store locally if a path is provided
    if store_path:
        store.save_local(store_path)

    return store


async def get_retriever(keywords: List[str], page: int):
    loader = DocumentLoader()
    docs = await loader.get_docs(keywords=keywords, page=page)
    vector_store = await create_vector_store(docs)
    if hasattr(vector_store, 'as_retriever'):
        # retriever = vector_store.as_retriever()
        # print(retriever.invoke("Summarize popular tweets about AI"))
        return vector_store.as_retriever()
    else:
        return vector_store


if __name__ == '__main__':
    import asyncio

    asyncio.run(get_retriever(["AI trends"], 1))
