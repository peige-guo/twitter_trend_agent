# XAgent: X (Twitter) Hotspots & Public Opinion Real-Time Analysis Agent

## Project Introduction
XAgent is a complex AI Agent application built on large models. This tool receives user input on the web front-end, and the back-end scrapes X (Twitter) data in real time. Based on the user's input, it queries real-time data, autonomously conducts data analysis, and generates precise responses or data analysis reports, which are then returned to the user through the front-end. For example, users can request:
- I am learning about AI trends. Please find the most liked and retweeted posts about AI and return the links along with your recommendations.
- I am preparing to post about the latest tech developments. Please generate a viral tweet based on current trending topics to help me gain more attention.

## Core Technology

**In terms of project architecture**, XAgent is an end-to-end service using a front-end/back-end separation architecture. The backend combines LangServe and FastAPI technologies, utilizing the LangServe's `add_routes` interface to encapsulate chains and RAG services from LangChain into REST APIs. It supports high-concurrency requests, streaming, and asynchronous operations. The frontend is built with Streamlit, focusing on simple user interaction rather than complex visual presentation. **In terms of technology application**, the core AI Agent framework is provided by LangGraph, and the basic model invocation is done through LangChain, supporting the most popular GPT series (international), GLM4 models (domestic), and DeepSeek models.

- **Technology Stack**

  - **AI Agent Framework**: LangGraph

  - **Model Invocation**: Supports mainstream online & open-source models through LangChain (GPT, GLM4, DeepSeek)

  - **Frontend Technology**: Streamlit

  - **Backend Technology**: LangServe + FastAPI

  - **Embedded Models**: OpenAI Embedding, GLM Embedding, DeepSeek Embedding

  - **State Tracking**: LangSmith


- **Complete Project Architecture**

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[User Interface<br/>Streamlit Client]
    end
    
    subgraph "API Gateway Layer"
        B[FastAPI + LangServe<br/>REST API Server<br/>Port: 8000]
    end
    
    subgraph "AI Agent Core - LangGraph Workflow"
        C[Entry Point<br/>User Query]
        D[Retrieve Node<br/>Fetch Twitter Data]
        E[Grade Documents Node<br/>Filter Relevant Tweets]
        F[Transform Query Node<br/>Rewrite Question]
        G[Generate Node<br/>Create Response]
        H[Edge Decision 1<br/>Documents Relevant?]
        I[Edge Decision 2<br/>Response Quality Check]
        J[END<br/>Return Result]
    end
    
    subgraph "Data Collection Layer"
        K[Twitter Scraper<br/>Twikit Library]
        L[Twitter API<br/>Real-time Data]
    end
    
    subgraph "Vector Storage & Retrieval"
        M[Document Loader<br/>Process Tweets]
        N[Text Splitter<br/>Chunk Size: 500]
        O[HuggingFace Embeddings<br/>all-MiniLM-L6-v2]
        P[FAISS Vector Store<br/>Similarity Search]
    end
    
    subgraph "LLM Layer"
        Q[Model Router]
        R[DeepSeek API<br/>deepseek-chat]
        S[OpenAI GPT<br/>GPT-3.5/4]
        T[GLM4<br/>Zhipu AI]
    end
    
    subgraph "Grading & Validation"
        U[Retrieval Grader<br/>Relevance Check]
        V[Hallucination Grader<br/>Fact Verification]
        W[Answer Evaluator<br/>Quality Assessment]
    end
    
    A -->|HTTP POST Request<br/>User Question| B
    B -->|Invoke LangGraph Chain| C
    C --> D
    D -->|Keywords Extraction| M
    M -->|Fetch Tweets| K
    K -->|Scrape Data| L
    L -->|Tweet Data| K
    K -->|Raw Tweets| M
    M -->|Convert to Documents| N
    N -->|Split Text| O
    O -->|Generate Embeddings| P
    P -->|Retrieved Documents| D
    D --> E
    E -->|Grade Each Document| U
    U -->|Relevance Score| H
    H -->|No Relevant Docs| F
    H -->|Has Relevant Docs| G
    F -->|Rewritten Query| D
    G -->|Use LLM| Q
    Q --> R
    Q --> S
    Q --> T
    R -->|Generated Text| G
    S -->|Generated Text| G
    T -->|Generated Text| G
    G -->|Check Quality| I
    I -->|Check Hallucination| V
    V -->|Validate Answer| W
    W -->|Not Useful| F
    W -->|Not Supported| G
    W -->|Useful| J
    J -->|JSON Response| B
    B -->|Stream Results| A
    A -->|Display Analysis<br/>+ Tweet Links| A

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#f0e1ff
    style G fill:#e1ffe1
    style J fill:#ffe1e1
    style Q fill:#ffe1f5
    style P fill:#f5ffe1
    style K fill:#e1fff5
```

<div align="center">
<i>This diagram shows the complete data flow from user input through Twitter scraping, vector storage, LLM processing, to final response generation</i>
</div>

- **Core Function Development Flowchart**


## Installation Guide

### Quick Start (All Platforms)
```bash
# Clone repository
git clone https://github.com/peige-guo/twitter_trend_agent.git
cd XAgent

# Install dependencies (10-100x faster than pip!)
uv pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Create .env file (or copy from .env.example and edit)
cat > .env << EOF
DEEPSEEK_API_KEY=your_key_here
model=deepseek-chat

# Twitter/X Authentication (REQUIRED for scraping)
TWITTER_USERNAME=your_twitter_username
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_twitter_password
EOF

# Run server (Terminal 1)
python app/server.py

# Run client (Terminal 2 - opens browser automatically)
streamlit run app/client.py
```







