#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: PG
# Date: 2025-10-15


from langchain_core.documents import Document
from twitter_tools import get_twitter
from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentLoader:
    """
    This class uses the get_docs function to take a Keyword as input, and outputs a list of documents (including metadata).
    """

    async def get_docs(self, keywords: List[str], page: int) -> List[Document]:
        """
        Asynchronously retrieves documents based on specific keywords by scraping X (Twitter).
        This function utilizes a pipeline to fetch and format tweet data, returning it as Document objects.

        Args:
        keywords (List[str]): A list of keywords used to search X (Twitter).
        page (int): The page number in the API request, used for pagination.

        Returns:
            List[Document]: A list of Document objects containing the retrieved content.
        """

        raw_docs = await get_twitter.twitter_detail_pipeline(keywords=keywords, page=page)

        docs = [Document(page_content=doc["real_data"]) for doc in raw_docs]

        return docs

    async def create_vector_store(self, docs, store_path: Optional[str] = None) -> Optional['FAISS']:
        """
        Creates a FAISS vector store from a list of documents.

        Args:
            docs (List[Document]): A list of Document objects containing the content to be stored.
            store_path (Optional[str]): The path to store the vector store locally. If None, the vector store will not be stored.

        Returns:
            Optional[FAISS]: The FAISS vector store containing the documents, or None if no documents are provided.
        """
        # Check if docs is empty
        if not docs:
            print("Warning: No documents provided to create vector store")
            return None
            
        # Perform text splitting and use HuggingFace Embedding model to generate vector representations
        # Tweets are shorter, so use smaller chunk size
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        texts = text_splitter.split_documents(docs)
        
        # Check if texts is empty after splitting
        if not texts:
            print("Warning: No text chunks created after splitting documents")
            return None
            
        # Use a lightweight, fast embedding model suitable for short texts like tweets
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        store = FAISS.from_documents(texts, embedding_model)

        if store_path:
            store.save_local(store_path)
        return store

    async def get_retriever(self, keywords: List[str], page: int):
        """
        Retrieves documents and returns a retriever based on the documents.

        Args:
            keywords (List[str]): Keywords to search documents.
            page (int): Page number for pagination of results.

        Returns:
            List[Document]: Retrieved documents, or empty list if no documents found.
        
        Raises:
            RuntimeError: If X (Twitter) access fails
        """
        print(f"Starting real-time scraping of X (Twitter) data")
        
        try:
            docs = await self.get_docs(keywords, page)
        except RuntimeError as e:
            # Propagate the "no access to X" error message
            print(f"Error: {str(e)}")
            raise RuntimeError(str(e))
        
        print(f"Received X (Twitter) data: {docs}")
        print("-------------------------")
        
        # If no documents were retrieved, return empty list
        if not docs:
            print("No documents retrieved from X (Twitter). Returning empty list.")
            return []
        
        print(f"Starting vector database storage")
        vector_store = await self.create_vector_store(docs)
        
        # If vector store creation failed, return empty list
        if vector_store is None:
            print("Failed to create vector store. Returning empty list.")
            return []
            
        print(f"Successfully completed vector database storage")
        print("-------------------------")
        print(f"Starting text retrieval")
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})
        retriever_result = retriever.invoke(str(keywords))
        print(f"Retrieved data: {retriever_result}")
        return retriever_result


if __name__ == '__main__':
    import asyncio

    # Create DocumentLoader instance and call get_docs
    async def main():
        loader = DocumentLoader()
        await loader.get_retriever(keywords=["AI trends"], page=1)

    asyncio.run(main())
