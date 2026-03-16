# Topic 5: AI Agents for Data Engineering - Complete Guide

## 📑 Table of Contents

### Part 1: Fundamentals
1. [AI Agents Overview](#1-ai-agents-overview)
2. [Understanding Your Data](#2-understanding-your-data-sample-raw-data)
3. [LLM Fundamentals](#3-llm-fundamentals)

### Part 2: Core Technologies
4. [Vector Databases](#4-vector-databases)
5. [RAG (Retrieval Augmented Generation)](#5-rag-retrieval-augmented-generation)
6. [Databricks ML & AI](#6-databricks-ml--ai)

### Part 3: Building AI Agents
7. [Building Chatbots](#7-building-chatbots)
8. [Data Engineering AI Agents](#8-data-engineering-ai-agents)
9. [Real-Time AI Agents](#9-real-time-ai-agents)

### Part 4: Advanced Topics
10. [Fine-Tuning LLMs](#10-fine-tuning-llms)
11. [Production Deployment](#11-production-deployment)
12. [Monitoring & Optimization](#12-monitoring--optimization)

### Part 5: Interview & Practical
13. [Interview Questions & Answers](#13-ai-agents-interview-questions--answers)
14. [System Design with AI Agents](#14-system-design-with-ai-agents)
15. [Hands-On Exercises](#15-hands-on-exercises)

---

## 🎯 Learning Goals

- What an AI agent is and how it uses an LLM + tools + (optionally) RAG
- LLM basics: prompts, **temperature** (0 = deterministic, 1 = creative), **max_tokens** (length cap)
- RAG: embed docs → vector DB → retrieve by query → prompt LLM with context
- Build a simple chatbot and a SQL-from-NL agent
- Deploy and monitor (latency, token usage, errors)

---

## 📖 Core Concepts

### 1. AI Agents Overview

**What is an AI Agent?**
A program that uses an LLM to understand input, decide what to do, and call tools (e.g., query a DB, run code) to get a result—instead of just answering from memory.

**Key parts**:
- **LLM (Large Language Model)**: Core reasoning engine
- **Vector Database**: Stores embeddings for retrieval
- **RAG System**: Retrieves relevant context
- **Orchestration**: Coordinates agent actions
- **Tools/APIs**: External integrations

**AI Agent Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              User Query                                  │
│  "What were sales last month?"                          │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Query Understanding        │
        │   (LLM analyzes intent)      │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   RAG System                  │
        │  ┌────────────────────────┐ │
        │  │  Vector Search          │ │
        │  │  (Find relevant docs)   │ │
        │  └───────────┬────────────┘ │
        │              ↓                │
        │  ┌────────────────────────┐ │
        │  │  Context Retrieval      │ │
        │  │  (Get relevant data)    │ │
        │  └───────────┬────────────┘ │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   LLM Processing              │
        │  ┌────────────────────────┐  │
        │  │  Generate Response     │  │
        │  │  (Using context)       │  │
        │  └───────────┬────────────┘  │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Action Execution            │
        │  ┌──────────┐  ┌──────────┐ │
        │  │  Query   │  │  Execute │ │
        │  │  Data    │  │  Code    │ │
        │  └──────────┘  └──────────┘ │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Response to User            │
        │  "Sales last month: $1.2M"   │
        └──────────────────────────────┘
```

**Types:** Single-turn; multi-turn with memory; tool-using (run code, query DBs); autonomous (multi-step plans).

**Data engineering use cases**:
- ✅ **Data Pipeline Chatbot**: Answer questions about pipelines
- ✅ **SQL Query Generator**: Generate SQL from natural language
- ✅ **Data Quality Monitor**: Detect and explain data issues
- ✅ **Documentation Assistant**: Auto-generate pipeline docs
- ✅ **Anomaly Detection**: Explain anomalies in data

---

### 2. Understanding Your Data: Sample Raw Data

**What the agent will work with** — example shapes of data and pipeline metadata:

**Sample sales row**:
```json
{
  "sale_id": "SALE-001",
  "customer_id": 101,
  "product_id": 501,
  "amount": 150.00,
  "sale_date": "2024-01-15",
  "store_id": 1,
  "region": "US"
}
```

**Sample pipeline metadata** (what we might store for RAG/docs):
```json
{
  "pipeline_name": "sales_etl",
  "source": "s3://nike-raw/sales/",
  "destination": "s3://nike-processed/sales/",
  "schedule": "daily",
  "last_run": "2024-01-15T02:00:00Z",
  "status": "success",
  "records_processed": 1000000
}
```

**Goals**: Answer pipeline questions, generate SQL, explain data quality issues, and automate data-engineering tasks.

---

### 3. LLM Fundamentals

**What is an LLM?**
A model trained on huge amounts of text that predicts the next tokens—used for understanding and generating language (chat, code, summaries).

**Common choices**:
- **OpenAI GPT-4**: Most capable, paid
- **Anthropic Claude**: Good for long context
- **Llama 2/3**: Open-source, self-hosted
- **Databricks DBRX**: Databricks' open-source model

**LLM Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Input Prompt                                │
│  "What were sales last month?"                         │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Tokenization                │
        │   (Convert text to tokens)    │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Embedding Layer            │
        │   (Convert to vectors)        │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Transformer Layers          │
        │   (Attention mechanism)       │
        │   - Self-attention            │
        │   - Feed-forward              │
        │   - Layer normalization       │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Output Generation           │
        │   (Generate tokens)           │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Response                   │
        │  "Sales last month: $1.2M"   │
        └──────────────────────────────┘
```

#### 3.1 Prompt Engineering

**What is it?** Writing clear instructions and examples so the LLM returns the right format and content.

**Typical order:** System (role/context) → User query → Context or examples → Output format.

**Basic Prompt Example**:
```python
prompt = """
You are a data engineering assistant.
Answer questions about data pipelines clearly and concisely.

User Question: What is the status of the sales pipeline?

Answer:
"""
```

**Few-Shot Prompting** (Examples):
```python
prompt = """
You are a SQL query generator. Generate SQL queries from natural language.

Example 1:
Question: Get all sales from January 2024
SQL: SELECT * FROM sales WHERE sale_date >= '2024-01-01' AND sale_date < '2024-02-01'

Example 2:
Question: Total revenue by customer
SQL: SELECT customer_id, SUM(amount) as total_revenue FROM sales GROUP BY customer_id

Question: Sales for customer 101 in the last 30 days
SQL:
"""
```

**Chain-of-thought** (ask for step-by-step reasoning):
```python
prompt = """
Analyze this data quality issue step by step:

Data Issue: Sales table has negative amounts

Step 1: Identify the problem
Step 2: Find root cause
Step 3: Suggest solution

Analysis:
"""
```

#### 3.2 Using LLMs in Databricks

**Install libraries**:
```python
%pip install openai langchain databricks-vectorsearch
```

**OpenAI call with parameter notes**:

| Parameter | What it does | Typical values |
|-----------|----------------|----------------|
| `temperature` | Randomness of output. Higher = more varied/creative; lower = more deterministic. | 0–0.3 for SQL/code; 0.7–0.9 for chat |
| `max_tokens` | Hard cap on length of the model’s reply (tokens ≈ words/4). | 500–2000 for short answers; 4000+ for long |
| `top_p` (optional) | Nucleus sampling: only sample from top tokens whose cumulative probability ≤ this. | 0.9–1.0; often used with or instead of temperature |

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a data engineering assistant."},
        {"role": "user", "content": "What is a data pipeline?"}
    ],
    temperature=0.7,   # Slightly creative, good for conversational answers
    max_tokens=500    # Limit response length; 500 ≈ 125–375 words
)

answer = response.choices[0].message.content
print(answer)
```

**Databricks foundation models** (same idea: control temperature and length):
```python
from langchain.llms import Databricks

llm = Databricks(
    endpoint_name="databricks-dbrx-instruct",
    model_kwargs={
        "temperature": 0.7,   # Same meaning as OpenAI: higher = more varied
        "max_tokens": 500     # Max length of generated response
    }
)

response = llm("What is a data pipeline?")
print(response)
```

**LangChain (wraps OpenAI; parameters are the same)**:
```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7    # LangChain passes this to the API; 0.7 = balanced for chat
)

messages = [
    SystemMessage(content="You are a data engineering assistant."),
    HumanMessage(content="What is a data pipeline?")
]

response = llm(messages)
print(response.content)
```

---

### 4. Vector Databases

**What is it?** A store for *embeddings* (numeric vectors from text). You search by “nearest vectors,” not by exact keywords.

**Why use one?** Fast similarity search by meaning (e.g., “sales pipeline status” matches “how does the ETL job run?”) and built for many dimensions (e.g., 1536).

**Vector Database Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              Documents/Text                              │
│  "Sales pipeline processes 1M records daily"          │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Embedding Model            │
        │   (Convert text to vector)   │
        │   [0.23, -0.45, 0.67, ...]   │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Vector Database            │
        │  ┌────────────────────────┐ │
        │  │  Store Vectors          │ │
        │  │  + Metadata             │ │
        │  │  + Original Text        │ │
        │  └───────────┬────────────┘ │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Query Vector               │
        │   [0.25, -0.43, 0.65, ...]   │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Similarity Search          │
        │   (Cosine similarity)         │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Top-K Results               │
        │   (Most similar documents)    │
        └──────────────────────────────┘
```

#### 4.1 Databricks Vector Search

**What is it?** Databricks’ managed service to store and query embeddings (no separate DB to run).

**Create Vector Search Index**:
```python
from databricks.vector_search.client import VectorSearchClient
from databricks.sdk import WorkspaceClient

# Initialize client
w = WorkspaceClient()
vsc = VectorSearchClient(workspace_client=w)

# Create endpoint
endpoint_name = "nike-data-embeddings"
vsc.create_endpoint(
    name=endpoint_name,
    endpoint_type="STANDARD"
)

# Create index — dimension must match your embedding model (e.g. text-embedding-3-small = 1536)
index_name = "pipeline-docs-index"
vsc.create_index(
    endpoint_name=endpoint_name,
    index_name=index_name,
    primary_key="doc_id",
    index_schema={
        "fields": [
            {"name": "doc_id", "type": "string"},
            {"name": "text", "type": "string"},
            {"name": "embedding", "type": "vector", "dimension": 1536}  # Must match embedding size
        ]
    }
)
```

**Generate Embeddings**:
```python
from langchain.embeddings import OpenAIEmbeddings

# Embedding model choice sets vector size (e.g. text-embedding-3-small → 1536 dims)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

doc_text = "Sales pipeline processes 1M records daily from S3 to Redshift"
doc_embedding = embeddings.embed_query(doc_text)

print(f"Embedding dimension: {len(doc_embedding)}")  # 1536 for this model
```

**Insert Documents**:
```python
import pandas as pd

# Sample documents
documents = [
    {
        "doc_id": "doc1",
        "text": "Sales pipeline processes 1M records daily from S3 to Redshift",
        "pipeline_name": "sales_etl",
        "category": "pipeline"
    },
    {
        "doc_id": "doc2",
        "text": "Customer pipeline runs hourly and loads data to Delta Lake",
        "pipeline_name": "customer_etl",
        "category": "pipeline"
    }
]

# Generate embeddings
for doc in documents:
    doc["embedding"] = embeddings.embed_query(doc["text"])

# Create DataFrame
df = pd.DataFrame(documents)

# Write to Delta table
df.write.format("delta").mode("overwrite").saveAsTable("pipeline_docs")

# Sync to vector index
vsc.upsert(
    endpoint_name=endpoint_name,
    index_name=index_name,
    inputs=documents
)
```

**Search Similar Documents**:
```python
# Query embedding
query = "How does the sales pipeline work?"
query_embedding = embeddings.embed_query(query)

# num_results (top_k): how many nearest neighbors to return; 3–5 is typical for RAG
results = vsc.similarity_search(
    endpoint_name=endpoint_name,
    index_name=index_name,
    query_vector=query_embedding,
    num_results=3
)

# Display results
for result in results:
    print(f"Score: {result['score']}")
    print(f"Text: {result['text']}")
    print(f"Metadata: {result.get('pipeline_name')}")
    print("---")
```

#### 4.2 Alternative Vector Databases

**Pinecone**:
```python
import pinecone

# Initialize Pinecone
pinecone.init(api_key="your-api-key", environment="us-east-1")

# Create index
index = pinecone.Index("pipeline-docs")

# Upsert vectors
vectors = [
    ("doc1", [0.23, -0.45, 0.67, ...], {"text": "Sales pipeline..."}),
    ("doc2", [0.25, -0.43, 0.65, ...], {"text": "Customer pipeline..."})
]
index.upsert(vectors=vectors)

# Query
query_vector = [0.24, -0.44, 0.66, ...]
results = index.query(vector=query_vector, top_k=3)
```

**Chroma**:
```python
import chromadb

# Initialize Chroma
client = chromadb.Client()

# Create collection
collection = client.create_collection("pipeline_docs")

# Add documents
collection.add(
    documents=["Sales pipeline processes 1M records...", "Customer pipeline runs hourly..."],
    ids=["doc1", "doc2"],
    metadatas=[{"pipeline": "sales"}, {"pipeline": "customer"}]
)

# Query
results = collection.query(
    query_texts=["How does sales pipeline work?"],
    n_results=2
)
```

---

### 5. RAG (Retrieval Augmented Generation)

**What is RAG?** First *retrieve* relevant docs (e.g., via vector search), then *generate* an answer with the LLM using that text as context.

**Why use it?** Cuts hallucinations, uses your current data/docs, and keeps answers grounded in what you actually have.

**RAG Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              User Query                                  │
│  "What is the status of sales pipeline?"               │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Step 1: Query Embedding     │
        │   (Convert query to vector)   │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Step 2: Vector Search       │
        │   (Find similar documents)    │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Step 3: Retrieve Context    │
        │   (Get top-K documents)       │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Step 4: Build Prompt        │
        │   (Query + Context)          │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Step 5: LLM Generation      │
        │   (Generate response)        │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Response                   │
        │  "Sales pipeline is running  │
        │   successfully, processing   │
        │   1M records daily..."       │
        └──────────────────────────────┘
```

#### 5.1 Building RAG System

**Step 1: Prepare Documents**:
```python
# Sample pipeline documentation
documents = [
    {
        "id": "doc1",
        "text": "Sales pipeline (sales_etl) processes 1M records daily from S3 to Redshift. Runs at 2 AM daily.",
        "metadata": {"pipeline": "sales_etl", "type": "pipeline"}
    },
    {
        "id": "doc2",
        "text": "Customer pipeline (customer_etl) runs hourly and loads data to Delta Lake. Last run: 2024-01-15 10:00:00",
        "metadata": {"pipeline": "customer_etl", "type": "pipeline"}
    }
]
```

**Step 2: Generate embeddings** (chunk first so each piece fits the embedding model and retrieval):
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

embeddings = OpenAIEmbeddings()

# chunk_size: max characters per chunk; 500 keeps context tight
# chunk_overlap: overlap between chunks so we don’t cut sentences in a bad place
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Split and embed
chunks = []
for doc in documents:
    splits = text_splitter.split_text(doc["text"])
    for i, split in enumerate(splits):
        chunk = {
            "id": f"{doc['id']}_chunk_{i}",
            "text": split,
            "embedding": embeddings.embed_query(split),
            "metadata": doc["metadata"]
        }
        chunks.append(chunk)
```

**Step 3: Store in Vector Database**:
```python
# Store in Databricks Vector Search
vsc.upsert(
    endpoint_name=endpoint_name,
    index_name=index_name,
    inputs=chunks
)
```

**Step 4: RAG query function** (with parameter notes):
```python
def rag_query(user_query: str, top_k: int = 3):
    """
    RAG: embed query → vector search → build prompt with context → LLM.
    """
    # Step 1: Same embedding model as index; turns query into a vector
    query_embedding = embeddings.embed_query(user_query)

    # Step 2: top_k = how many chunks to retrieve; 3–5 is common
    results = vsc.similarity_search(
        endpoint_name=endpoint_name,
        index_name=index_name,
        query_vector=query_embedding,
        num_results=top_k   # More = more context but noisier and slower
    )

    # Step 3: One string of context for the prompt
    context = "\n\n".join([r["text"] for r in results])

    prompt = f"""You are a data engineering assistant. Answer using only the context below.

Context:
{context}

Question: {user_query}

If the answer is not in the context, say "I don't have that information."
"""

    # Step 4: LLM call — temperature 0.7 for natural answers; add max_tokens if needed
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful data engineering assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,   # Slightly creative; for strict factual answers use 0.2–0.3
        max_tokens=500    # Optional: cap length so responses don’t run long
    )

    return response.choices[0].message.content

# Example
answer = rag_query("What is the status of sales pipeline?")
print(answer)
```

**Step 5: RAG with metadata filter** (e.g., only docs for one pipeline):
```python
def rag_query_with_filter(user_query: str, pipeline_name: str = None):
    query_embedding = embeddings.embed_query(user_query)

    results = vsc.similarity_search(
        endpoint_name=endpoint_name,
        index_name=index_name,
        query_vector=query_embedding,
        num_results=3,
        filters={"pipeline": pipeline_name} if pipeline_name else None  # Restrict by metadata
    )

    context = "\n\n".join([r["text"] for r in results])
    prompt = f"""Context:\n{context}\n\nQuestion: {user_query}\nAnswer:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7   # Same as above: balance between focused and natural
    )

    return response.choices[0].message.content
```

---

### 6. Databricks ML & AI

**Relevant pieces**: MLflow (track/deploy models), Vector Search (embeddings), Foundation Models (hosted LLMs), ML Runtime (preconfigured env).

**MLflow Integration**:
```python
import mlflow
from mlflow.tracking import MlflowClient

# Log LLM model
with mlflow.start_run():
    mlflow.log_param("model", "gpt-4")
    mlflow.log_param("temperature", 0.7)
    
    # Log prompt template
    prompt_template = """
    You are a data engineering assistant.
    Question: {question}
    Answer:
    """
    mlflow.log_text(prompt_template, "prompt_template.txt")
    
    # Log metrics
    mlflow.log_metric("response_time", 1.2)
```

**Databricks Foundation Models** (parameter meanings same as before):
```python
from langchain.llms import Databricks

llm = Databricks(
    endpoint_name="databricks-dbrx-instruct",
    model_kwargs={
        "temperature": 0.7,   # 0 = deterministic; 1 = more random
        "max_tokens": 500     # Stops generation after this many tokens
    }
)

response = llm("What is a data pipeline?")
print(response)
```

---

### 7. Building Chatbots

**What is it?** An agent that keeps conversation history and replies in natural language (often with RAG or tools).

**Chatbot Architecture Flow**:
```
┌─────────────────────────────────────────────────────────┐
│              User Message                                │
│  "What is the status of sales pipeline?"               │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   Message History             │
        │   (Conversation context)      │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Intent Classification       │
        │   (Understand user intent)    │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   RAG Retrieval               │
        │   (Get relevant context)       │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   LLM Generation               │
        │   (Generate response)          │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Response to User            │
        │  "Sales pipeline is running   │
        │   successfully..."           │
        └──────────────────────────────┘
```

#### 7.1 Simple Chatbot

**Basic Chatbot**:
```python
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# LLM: temperature 0.7 = natural chat; use 0.2–0.3 for more deterministic (e.g. tool choice)
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

# Initialize memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Simple chatbot function
def chatbot(user_message: str, chat_history: list = []):
    """
    Simple chatbot with conversation history
    """
    # Build messages with history
    messages = [
        {"role": "system", "content": "You are a helpful data engineering assistant."}
    ]
    
    # Add conversation history
    for msg in chat_history:
        messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": user_message})
    
    # temperature=0.7: good for multi-turn chat; history already gives context
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=1024   # Allow longer replies when explaining pipelines
    )
    
    assistant_message = response.choices[0].message.content
    
    # Update history
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message, chat_history

# Example usage
chat_history = []
response, chat_history = chatbot("What is a data pipeline?", chat_history)
print(response)

response, chat_history = chatbot("How does it work?", chat_history)
print(response)
```

#### 7.2 RAG-Powered Chatbot

**RAG Chatbot with Vector Search**:
```python
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import DatabricksVectorSearch

# Initialize vector store
vector_store = DatabricksVectorSearch(
    endpoint=endpoint_name,
    index=index_name
)

# Create RAG chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    memory=memory,
    return_source_documents=True
)

def rag_chatbot(question: str):
    """
    RAG-powered chatbot
    """
    result = qa_chain({"question": question})
    
    return {
        "answer": result["answer"],
        "sources": [doc.page_content for doc in result["source_documents"]]
    }

# Example usage
result = rag_chatbot("What is the status of sales pipeline?")
print(f"Answer: {result['answer']}")
print(f"\nSources:")
for source in result['sources']:
    print(f"- {source}")
```

#### 7.3 Tool-Using Chatbot

**Chatbot with Database Query Tool**:
```python
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import DuckDuckGoSearchRun

def query_pipeline_status(pipeline_name: str) -> str:
    """
    Tool: Query pipeline status from database
    """
    # Simulate database query
    status = {
        "sales_etl": "running",
        "customer_etl": "success"
    }
    return f"Pipeline {pipeline_name} status: {status.get(pipeline_name, 'unknown')}"

def query_data_quality(table_name: str) -> str:
    """
    Tool: Query data quality metrics
    """
    # Simulate data quality check
    return f"Table {table_name} has 99.5% data quality score"

# Define tools
tools = [
    Tool(
        name="PipelineStatus",
        func=lambda x: query_pipeline_status(x),
        description="Query the status of a data pipeline. Input should be pipeline name."
    ),
    Tool(
        name="DataQuality",
        func=lambda x: query_data_quality(x),
        description="Query data quality metrics for a table. Input should be table name."
    )
]

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
response = agent.run("What is the status of sales_etl pipeline?")
print(response)
```

---

### 8. Data Engineering AI Agents

**What are they?** Agents that do data-engineering tasks: generate SQL, explain pipeline failures, summarize data quality, document pipelines, or explain anomalies.

#### 8.1 SQL Query Generator Agent

**SQL from natural language** (parameters matter a lot here):
```python
def sql_generator_agent(user_query: str, schema_info: str) -> str:
    """
    Generate SQL from natural language. Use low temperature so output is stable and correct.
    """
    prompt = f"""You are a SQL query generator. Generate SQL from natural language.

Database Schema:
{schema_info}

Examples:
Question: Get all sales from January 2024
SQL: SELECT * FROM sales WHERE sale_date >= '2024-01-01' AND sale_date < '2024-02-01'

Question: Total revenue by customer
SQL: SELECT customer_id, SUM(amount) as total_revenue FROM sales GROUP BY customer_id

Question: {user_query}
SQL:
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a SQL expert. Generate only SQL queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,   # Low = deterministic; critical for SQL (same question → same query)
        max_tokens=500    # SQL rarely needs more; prevents long rambling
    )
    
    sql_query = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    
    return sql_query.strip()

# Schema information
schema = """
Table: sales
Columns:
- sale_id (VARCHAR)
- customer_id (BIGINT)
- product_id (BIGINT)
- amount (DECIMAL)
- sale_date (DATE)
- store_id (INT)
"""

# Generate SQL
sql = sql_generator_agent("Get total sales for customer 101 in January 2024", schema)
print(sql)
# Output: SELECT SUM(amount) as total_sales FROM sales WHERE customer_id = 101 AND sale_date >= '2024-01-01' AND sale_date < '2024-02-01'
```

**Execute SQL with Validation**:
```python
def execute_sql_safely(sql_query: str, spark):
    """
    Execute SQL query with safety checks
    """
    # Safety checks
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
    if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
        return "Error: Query contains dangerous operations. Only SELECT queries are allowed."
    
    try:
        # Execute query
        result = spark.sql(sql_query)
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Complete SQL agent
def sql_agent(user_query: str, spark, schema_info: str):
    """
    Complete SQL agent: Generate and execute SQL
    """
    # Step 1: Generate SQL
    sql = sql_generator_agent(user_query, schema_info)
    print(f"Generated SQL: {sql}")
    
    # Step 2: Execute SQL
    result = execute_sql_safely(sql, spark)
    
    # Step 3: Format response
    if isinstance(result, str):
        return result
    else:
        # Convert to natural language
        prompt = f"""Explain this SQL result in natural language:

SQL Query: {sql}
Result: {result.show(10)}

Explanation:
"""
        explanation = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,   # Natural language explanation; a bit of variety is fine
            max_tokens=300
        )
        return explanation.choices[0].message.content
```

#### 8.2 Pipeline Monitor Agent

**Agent that Monitors and Explains Pipeline Failures**:
```python
def pipeline_monitor_agent(pipeline_name: str, pipeline_logs: str) -> str:
    """
    Monitor pipeline and explain failures
    """
    prompt = f"""You are a data pipeline monitoring agent. Analyze pipeline logs and explain any issues.

Pipeline: {pipeline_name}
Logs:
{pipeline_logs}

Analyze the logs and:
1. Identify if pipeline succeeded or failed
2. If failed, explain the root cause
3. Suggest solutions
4. Estimate impact

Analysis:
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data engineering expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,   # Low: we want consistent, factual analysis of logs
        max_tokens=800    # Enough for cause + solution + impact
    )

    return response.choices[0].message.content

# Example
logs = """
2024-01-15 02:00:00 - Pipeline started
2024-01-15 02:05:00 - Reading from s3://nike-raw/sales/
2024-01-15 02:10:00 - ERROR: OutOfMemoryError
2024-01-15 02:10:05 - Pipeline failed
"""

analysis = pipeline_monitor_agent("sales_etl", logs)
print(analysis)
```

#### 8.3 Data Quality Agent

**Agent that Detects and Explains Data Quality Issues**:
```python
def data_quality_agent(table_name: str, quality_metrics: dict) -> str:
    """
    Analyze data quality and explain issues
    """
    prompt = f"""You are a data quality analyst. Analyze data quality metrics and explain issues.

Table: {table_name}
Quality Metrics:
{quality_metrics}

Analyze:
1. Overall data quality score
2. Specific issues found
3. Impact of issues
4. Recommendations

Analysis:
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,   # Analytical output: stick to the metrics, minimal creativity
        max_tokens=600
    )

    return response.choices[0].message.content

# Example
metrics = {
    "total_records": 1000000,
    "null_percentage": 2.5,
    "duplicate_percentage": 0.1,
    "invalid_dates": 50,
    "negative_amounts": 10
}

analysis = data_quality_agent("sales", metrics)
print(analysis)
```

---

### 9. Real-Time AI Agents

**Ideas:** Analyze streaming batches, detect + explain anomalies, explain alerts in real time. Pattern: stream → aggregate or detect → optional LLM call to explain.

#### 9.1 Streaming Data Analysis Agent

**Agent for Real-Time Streaming Analysis**:
```python
from pyspark.sql import SparkSession
from pyspark.sql.streaming import StreamingQuery

def streaming_analysis_agent(spark: SparkSession):
    """
    Real-time streaming analysis agent
    """
    # Read streaming data
    stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "sales") \
        .load()
    
    # Process in batches
    def process_batch(batch_df, batch_id):
        """
        Process each batch with AI agent
        """
        # Aggregate data
        summary = batch_df.groupBy("customer_id") \
            .agg({"amount": "sum", "sale_id": "count"}) \
            .collect()
        
        # Analyze with LLM
        prompt = f"""Analyze this sales batch data:

{summary}

Identify:
1. Top customers
2. Anomalies
3. Trends
4. Recommendations

Analysis:
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,   # Exploratory analysis; some variation is OK
            max_tokens=500
        )

        analysis = response.choices[0].message.content
        print(f"Batch {batch_id} Analysis:\n{analysis}")
    
    # Write stream
    query = stream_df.writeStream \
        .foreachBatch(process_batch) \
        .start()
    
    return query
```

#### 9.2 Anomaly Detection Agent

**Agent that Detects and Explains Anomalies**:
```python
def anomaly_detection_agent(data_point: dict, historical_data: list) -> dict:
    """
    Detect and explain anomalies in real-time
    """
    prompt = f"""You are an anomaly detection agent. Analyze this data point against historical data.

Current Data Point:
{data_point}

Historical Data (last 10 points):
{historical_data}

Determine:
1. Is this an anomaly? (Yes/No)
2. Why is it an anomaly?
3. What could cause this?
4. What should be done?

Analysis:
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,   # We want consistent, factual explanation of why it’s an anomaly
        max_tokens=400
    )

    analysis = response.choices[0].message.content
    return {
        "is_anomaly": "Yes" in analysis,
        "explanation": analysis
    }

# Example
current = {"sales": 50000, "timestamp": "2024-01-15 10:00:00"}
historical = [
    {"sales": 10000, "timestamp": "2024-01-15 09:00:00"},
    {"sales": 12000, "timestamp": "2024-01-15 08:00:00"},
    # ... more historical data
]

result = anomaly_detection_agent(current, historical)
print(result)
```

---

### 10. Fine-Tuning LLMs

**What is it?** Further training a pre-trained LLM on your own examples so it’s better at your task and vocabulary.

**When it’s worth it:** Your domain has specific terms, you need a fixed output format, or you want better accuracy/cost with a smaller model.

**Fine-Tuning Process**:
```python
# Prepare training data
training_data = [
    {
        "prompt": "What is the status of sales pipeline?",
        "completion": "Sales pipeline (sales_etl) is running successfully, processing 1M records daily."
    },
    {
        "prompt": "How many records does customer pipeline process?",
        "completion": "Customer pipeline (customer_etl) processes 500K records hourly."
    }
    # ... more examples
]

# Fine-tune with OpenAI
import openai

# Upload training file
with open("training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

# Create fine-tuning job
response = openai.FineTuningJob.create(
    training_file="file-abc123",
    model="gpt-3.5-turbo",
    hyperparameters={
        "n_epochs": 3,                    # Passes over the training data; more = risk overfitting
        "learning_rate_multiplier": 1.0   # 1.0 = default; lower = gentler updates
    }
)

# Use fine-tuned model
fine_tuned_model = "ft:gpt-3.5-turbo:org:custom-model:abc123"
response = client.chat.completions.create(
    model=fine_tuned_model,
    messages=[{"role": "user", "content": "What is the status of sales pipeline?"}]
)
```

---

### 11. Production Deployment

**Deploying in production:** Serve the agent as a model (e.g. MLflow), expose an API, or use a Databricks serving endpoint.

**1. Model serving with MLflow**:
```python
import mlflow
import mlflow.pyfunc

# Log model
class DataEngineeringAgent(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input):
        # Agent logic
        return agent_response

mlflow.pyfunc.log_model(
    "agent_model",
    python_model=DataEngineeringAgent()
)

# Serve model
mlflow.pyfunc.serve_model(
    model_uri="models:/data_engineering_agent/1",
    host="0.0.0.0",
    port=5000
)
```

**2. API Endpoint**:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    response = chatbot(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**3. Databricks Serving Endpoint**:
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Create serving endpoint
w.serving_endpoints.create(
    name="data-engineering-agent",
    config={
        "served_models": [{
            "model_name": "data_engineering_agent",
            "model_version": "1",
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }]
    }
)
```

---

### 12. Monitoring & Optimization

**What to track:** Latency, token usage (input + output), errors, and optionally user feedback. Log sample prompts/responses for debugging.
```python
import mlflow

mlflow.log_metric("response_time", 1.2)
mlflow.log_metric("token_usage", 500)   # Drives cost; monitor per request
mlflow.log_text(prompt, "prompt.txt")
mlflow.log_text(response, "response.txt")
```

**Cost:** Use smaller/cheaper models where possible, cache frequent queries, set `max_tokens`, consider fine-tuned smaller models.

---

### 13. AI Agents Interview Questions & Answers

#### Q1: Explain RAG Architecture

**Question**: "Explain how RAG (Retrieval Augmented Generation) works. Walk me through the architecture."

**Answer Structure**:

**1. What is RAG?** Retrieve relevant docs (e.g. vector search), then generate an answer with the LLM using that as context.

**2. Flow**:
```
User Query → Embed Query → Vector Search → Retrieve Context → Build Prompt → LLM Generation → Response
```

**3. Detailed Architecture**:

**Step 1: Query Embedding**:
```python
# Convert user query to vector
query = "What is the status of sales pipeline?"
query_embedding = embeddings.embed_query(query)
# Output: [0.23, -0.45, 0.67, ...] (1536 dimensions)
```

**Step 2: Vector Search**:
```python
# Search for similar documents
results = vector_db.similarity_search(
    query_vector=query_embedding,
    top_k=3
)
# Returns: Top 3 most similar documents
```

**Step 3: Context Retrieval**:
```python
# Extract text from results
context = "\n\n".join([doc.text for doc in results])
```

**Step 4: Prompt Building**:
```python
prompt = f"""Context:
{context}

Question: {query}

Answer based on the context above.
"""
```

**Step 5: LLM Generation**:
```python
response = llm.generate(prompt)
# Uses context to generate accurate response
```

**4. Key Components**:
- **Embedding Model**: Converts text to vectors (e.g., OpenAI text-embedding-3-small)
- **Vector Database**: Stores and searches embeddings (e.g., Databricks Vector Search)
- **Retriever**: Finds relevant documents (top-K similarity search)
- **LLM**: Generates response using context (e.g., GPT-4)

**5. Why RAG?** Reduces hallucinations, uses your current data, and grounds answers in retrieved docs.

**6. Real-World Example**:

**Scenario**: Data engineering chatbot

```python
# User asks: "What is the status of sales pipeline?"

# Step 1: Embed query
query_embedding = embeddings.embed_query("What is the status of sales pipeline?")

# Step 2: Search vector DB
results = vector_search(query_embedding, top_k=3)
# Returns:
# - "Sales pipeline (sales_etl) is running successfully, processing 1M records daily."
# - "Sales pipeline runs at 2 AM daily and loads data to Redshift."
# - "Last run: 2024-01-15 02:00:00, Status: Success"

# Step 3: Build prompt with context
prompt = f"""Context:
Sales pipeline (sales_etl) is running successfully, processing 1M records daily.
Sales pipeline runs at 2 AM daily and loads data to Redshift.
Last run: 2024-01-15 02:00:00, Status: Success

Question: What is the status of sales pipeline?

Answer:
"""

# Step 4: Generate response
response = llm.generate(prompt)
# Output: "The sales pipeline (sales_etl) is running successfully. It processes 1M records daily, runs at 2 AM, and the last run on 2024-01-15 was successful."
```

**Key Points**:
- ✅ RAG = Retrieval + Generation
- ✅ Vector search finds relevant context
- ✅ LLM uses context to generate accurate responses
- ✅ Reduces hallucinations significantly

---

#### Q2: How Do You Choose a Vector Database?

**Question**: "How do you choose between different vector databases? What factors matter?"

**Answer Structure**:

**1. Vector Database Options**:

| Database | Type | Pros | Cons |
|----------|------|------|------|
| **Databricks Vector Search** | Managed | Integrated, scalable | Databricks-only |
| **Pinecone** | Managed | Easy, fast | Cost at scale |
| **Chroma** | Self-hosted | Free, flexible | Requires maintenance |
| **Weaviate** | Self-hosted | Feature-rich | Complex setup |
| **Qdrant** | Self-hosted | Fast, efficient | Self-hosted overhead |

**2. Decision Framework**:

**Factor 1: Managed vs Self-Hosted**:

**Managed (Databricks Vector Search, Pinecone)**:
- ✅ No infrastructure management
- ✅ Auto-scaling
- ✅ Easy to use
- ❌ Less control
- ❌ Higher cost at scale

**Self-Hosted (Chroma, Weaviate)**:
- ✅ Full control
- ✅ Lower cost
- ✅ Customizable
- ❌ Requires maintenance
- ❌ Setup complexity

**Factor 2: Scalability**:

**Questions to Ask**:
- How many vectors? (millions vs billions)
- Query throughput? (QPS requirements)
- Growth rate? (how fast will it grow)

**Example**:
```python
# Small scale (< 1M vectors): Chroma or Pinecone
# Medium scale (1M-100M): Databricks Vector Search or Pinecone
# Large scale (> 100M): Databricks Vector Search or self-hosted cluster
```

**Factor 3: Integration**:

**Databricks Stack**:
- ✅ Use Databricks Vector Search (seamless integration)
- ✅ Works with Delta tables
- ✅ Integrated with MLflow

**AWS Stack**:
- ✅ Consider Pinecone (managed)
- ✅ Or self-host Chroma on EC2

**Factor 4: Cost**:

**Cost Comparison** (approximate):
- **Pinecone**: $70/month for 1M vectors
- **Databricks Vector Search**: Included in Databricks (pay for compute)
- **Chroma**: Free (self-hosted, pay for infrastructure)

**3. Real-World Decision**:

**Scenario**: Data engineering chatbot for 10K documents

**Requirements**:
- 10K documents (~1M vectors with chunking)
- 100 queries/day
- Databricks environment
- Need quick setup

**Decision**: **Databricks Vector Search**
- ✅ Integrated with existing stack
- ✅ No additional infrastructure
- ✅ Easy to set up
- ✅ Scales automatically

**Implementation**:
```python
# Use Databricks Vector Search
vsc = VectorSearchClient(workspace_client=w)
vsc.create_endpoint(name="pipeline-docs")
vsc.create_index(endpoint_name="pipeline-docs", index_name="docs-index", ...)
```

**4. Recommendation Matrix**:

| Scenario | Recommendation |
|----------|----------------|
| **Databricks user, < 10M vectors** | Databricks Vector Search |
| **Quick start, managed** | Pinecone |
| **Cost-sensitive, self-hosted OK** | Chroma |
| **Large scale (> 100M vectors)** | Databricks Vector Search or self-hosted cluster |
| **Feature-rich, self-hosted** | Weaviate |

**Key Points**:
- ✅ Consider managed vs self-hosted
- ✅ Evaluate scalability needs
- ✅ Check integration with existing tools
- ✅ Factor in cost at scale

---

#### Q3: Design an AI Agent for SQL Generation

**Question**: "Design an AI agent that generates SQL queries from natural language. Walk me through the architecture."

**Answer Structure**:

**1. Requirements**:
- Input: Natural language query
- Output: Valid SQL query
- Safety: Only SELECT queries
- Validation: Check SQL syntax
- Execution: Execute and return results

**2. Architecture**:

```
User Query → Intent Classification → Schema Retrieval → SQL Generation → Validation → Execution → Response
```

**3. Implementation**:

**Step 1: Intent Classification**:
```python
def classify_intent(query: str) -> str:
    """
    Classify user intent (SELECT, EXPLAIN, etc.)
    """
    prompt = f"""Classify this query intent:
Query: {query}

Intent (SELECT, EXPLAIN, DESCRIBE):
"""
    response = llm.generate(prompt)
    return response.strip()
```

**Step 2: Schema Retrieval**:
```python
def get_schema(table_name: str) -> str:
    """
    Get table schema from metadata
    """
    schema = spark.sql(f"DESCRIBE TABLE {table_name}").collect()
    return "\n".join([f"{row.col_name} ({row.data_type})" for row in schema])
```

**Step 3: SQL Generation**:
```python
def generate_sql(user_query: str, schema: str) -> str:
    """
    Generate SQL from natural language
    """
    prompt = f"""You are a SQL expert. Generate SQL queries from natural language.

Database Schema:
{schema}

Examples:
Question: Get all sales from January 2024
SQL: SELECT * FROM sales WHERE sale_date >= '2024-01-01' AND sale_date < '2024-02-01'

Question: Total revenue by customer
SQL: SELECT customer_id, SUM(amount) as total_revenue FROM sales GROUP BY customer_id

Question: {user_query}
SQL:
"""
    response = llm.generate(prompt, temperature=0.3)  # Low temp for stable, correct SQL
    sql = extract_sql(response)
    return sql
```

**Step 4: Validation**:
```python
def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate SQL query
    """
    # Check for dangerous operations
    dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE"]
    if any(keyword in sql.upper() for keyword in dangerous):
        return False, "Only SELECT queries are allowed"
    
    # Check syntax
    try:
        spark.sql(f"EXPLAIN {sql}")
        return True, "Valid SQL"
    except Exception as e:
        return False, str(e)
```

**Step 5: Execution**:
```python
def execute_sql(sql: str, spark) -> pd.DataFrame:
    """
    Execute SQL and return results
    """
    result = spark.sql(sql)
    return result.toPandas()
```

**4. Complete Agent**:
```python
def sql_agent(user_query: str, spark) -> dict:
    """
    Complete SQL generation agent
    """
    # Step 1: Classify intent
    intent = classify_intent(user_query)
    if intent != "SELECT":
        return {"error": "Only SELECT queries are supported"}
    
    # Step 2: Get schema (assume sales table)
    schema = get_schema("sales")
    
    # Step 3: Generate SQL
    sql = generate_sql(user_query, schema)
    
    # Step 4: Validate
    is_valid, message = validate_sql(sql)
    if not is_valid:
        return {"error": message, "sql": sql}
    
    # Step 5: Execute
    try:
        result = execute_sql(sql, spark)
        return {
            "sql": sql,
            "result": result.to_dict(),
            "row_count": len(result)
        }
    except Exception as e:
        return {"error": str(e), "sql": sql}
```

**5. Example Usage**:
```python
# User query
query = "Get total sales for customer 101 in January 2024"

# Agent response
result = sql_agent(query, spark)
# Returns:
# {
#   "sql": "SELECT SUM(amount) as total_sales FROM sales WHERE customer_id = 101 AND sale_date >= '2024-01-01' AND sale_date < '2024-02-01'",
#   "result": [{"total_sales": 1500.00}],
#   "row_count": 1
# }
```

**Key Points**:
- ✅ Intent classification
- ✅ Schema-aware generation
- ✅ Safety validation
- ✅ Error handling
- ✅ Result formatting

---

#### Q4: How Do You Handle LLM Hallucinations?

**Question**: "LLMs sometimes make up facts. How do you prevent hallucinations in your AI agents?"

**Answer Structure**:

**1. What are hallucinations?** The model outputs plausible-sounding but false or unsupported information.

**2. Prevention Strategies**:

**Strategy 1: Use RAG** (Most Effective):
```python
# Instead of asking LLM directly, use RAG
# LLM only uses retrieved context

def rag_query(query: str):
    # Retrieve relevant context
    context = vector_search(query, top_k=3)
    
    # Build prompt with context
    prompt = f"""Context:
{context}

Question: {query}

Answer based ONLY on the context above. If answer is not in context, say "I don't know".
"""
    return llm.generate(prompt)
```

**Strategy 2: Prompt Engineering**:
```python
# Explicit instructions to be accurate
prompt = """You are a data engineering assistant. 
IMPORTANT: Only use information from the provided context.
If you don't know the answer, say "I don't have that information."
Do not make up facts.

Context: {context}
Question: {query}
"""
```

**Strategy 3: Fact-Checking**:
```python
def fact_check_response(response: str, sources: list) -> bool:
    """
    Verify response against sources
    """
    # Check if response facts are in sources
    for source in sources:
        if response.lower() in source.lower():
            return True
    return False
```

**Strategy 4: Confidence Scoring**:
```python
def generate_with_confidence(query: str) -> dict:
    """
    Generate response with confidence score
    """
    response = llm.generate(query)
    
    # Ask LLM for confidence
    confidence_prompt = f"""Rate your confidence in this answer (0-1):
Answer: {response}
Confidence:
"""
    confidence = float(llm.generate(confidence_prompt))
    
    return {
        "response": response,
        "confidence": confidence,
        "should_verify": confidence < 0.7
    }
```

**3. Real-World Example**:

**Problem**: LLM makes up pipeline status

**Solution**: Use RAG with pipeline metadata

```python
# Bad: Direct LLM query (can hallucinate)
response = llm.generate("What is the status of sales pipeline?")
# Might say: "Sales pipeline is running" (even if it's not)

# Good: RAG query (grounded in real data)
def get_pipeline_status(pipeline_name: str):
    # Retrieve actual pipeline metadata
    metadata = get_pipeline_metadata(pipeline_name)
    
    # Use RAG
    context = f"Pipeline {pipeline_name}: Status={metadata['status']}, Last run={metadata['last_run']}"
    
    prompt = f"""Context:
{context}

Question: What is the status of {pipeline_name}?

Answer:
"""
    return llm.generate(prompt)
# Always accurate because it uses real metadata
```

**Key Points**:
- ✅ Use RAG (most effective)
- ✅ Explicit prompt instructions
- ✅ Fact-checking
- ✅ Confidence scoring
- ✅ Ground responses in real data

---

#### Q5: Design a Real-Time Anomaly Detection Agent

**Question**: "Design an AI agent that detects and explains anomalies in streaming data in real-time."

**Answer Structure**:

**1. Requirements**:
- Real-time streaming data
- Detect anomalies
- Explain why it's an anomaly
- Alert on anomalies

**2. Architecture**:

```
Streaming Data → Feature Extraction → Anomaly Detection → LLM Explanation → Alert
```

**3. Implementation**:

**Step 1: Feature Extraction**:
```python
def extract_features(data_point: dict) -> dict:
    """
    Extract features for anomaly detection
    """
    return {
        "sales": data_point["amount"],
        "timestamp": data_point["timestamp"],
        "customer_id": data_point["customer_id"],
        "hour_of_day": pd.to_datetime(data_point["timestamp"]).hour,
        "day_of_week": pd.to_datetime(data_point["timestamp"]).dayofweek
    }
```

**Step 2: Statistical Anomaly Detection**:
```python
def detect_anomaly(features: dict, historical_stats: dict) -> bool:
    """
    Detect if data point is anomaly
    """
    # Z-score method
    mean = historical_stats["mean"]
    std = historical_stats["std"]
    z_score = abs((features["sales"] - mean) / std)
    
    return z_score > 3  # 3 standard deviations
```

**Step 3: LLM Explanation**:
```python
def explain_anomaly(data_point: dict, historical_data: list) -> str:
    """
    Use LLM to explain why it's an anomaly
    """
    prompt = f"""You are a data analyst. Explain why this data point is an anomaly.

Current Data Point:
{data_point}

Historical Data (last 10 points):
{historical_data}

Explain:
1. Why is this an anomaly?
2. What patterns does it break?
3. What could cause this?
4. What should be done?

Analysis:
"""
    return llm.generate(prompt)
```

**4. Complete Agent**:
```python
def anomaly_detection_agent(stream_df, spark):
    """
    Real-time anomaly detection agent
    """
    historical_stats = calculate_historical_stats(spark)
    
    def process_batch(batch_df, batch_id):
        for row in batch_df.collect():
            features = extract_features(row.asDict())
            
            # Detect anomaly
            is_anomaly = detect_anomaly(features, historical_stats)
            
            if is_anomaly:
                # Explain with LLM
                explanation = explain_anomaly(row.asDict(), get_recent_data(spark))
                
                # Alert
                send_alert({
                    "anomaly": True,
                    "data_point": row.asDict(),
                    "explanation": explanation,
                    "timestamp": datetime.now()
                })
    
    query = stream_df.writeStream \
        .foreachBatch(process_batch) \
        .start()
    
    return query
```

**Key Points**:
- ✅ Real-time processing
- ✅ Statistical detection
- ✅ LLM explanation
- ✅ Alerting system

---

### 14. System Design with AI Agents

#### 14.1 Data Engineering Chatbot Architecture

**Complete Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│              User (Web/Mobile/API)                       │
└──────────────────────────┬──────────────────────────────┘
                           ↓
        ┌──────────────────────────────┐
        │   API Gateway                 │
        │   (Authentication, Rate Limit) │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Lambda Function             │
        │   (Orchestration)             │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Intent Classification       │
        │   (Understand user intent)    │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   RAG System                  │
        │  ┌────────────────────────┐ │
        │  │  Vector Search          │ │
        │  │  (Find relevant docs)   │ │
        │  └───────────┬────────────┘ │
        │              ↓                │
        │  ┌────────────────────────┐ │
        │  │  Context Retrieval      │ │
        │  └───────────┬────────────┘ │
        └──────────────┼───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   LLM (GPT-4/Claude)          │
        │   (Generate Response)         │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Response to User            │
        └──────────────────────────────┘
```

**Components**:
- **API Gateway**: Handle requests, authentication
- **Lambda**: Orchestrate agent workflow
- **RAG System**: Retrieve relevant context
- **Vector DB**: Store embeddings (Databricks Vector Search)
- **LLM**: Generate responses (OpenAI GPT-4)

**Implementation**:
```python
# API Gateway → Lambda
def lambda_handler(event, context):
    user_query = event["query"]
    
    # RAG query
    response = rag_chatbot(user_query)
    
    return {
        "statusCode": 200,
        "body": json.dumps({"response": response})
    }
```

#### 14.2 SQL Generation Agent Architecture

**Architecture**:
```
User Query → SQL Agent → Schema Retrieval → SQL Generation → Validation → Execution → Response
```

**Components**:
- **SQL Agent**: Orchestrates workflow
- **Schema Store**: Metadata database
- **SQL Generator**: LLM generates SQL
- **Validator**: Checks SQL safety
- **Executor**: Runs SQL on Spark/Redshift

---

### 15. Hands-On Exercises

#### Exercise 1: Build Simple RAG System

**Objective**: Build a basic RAG system from scratch

**Tasks**:
1. Prepare 10 documents about data pipelines
2. Generate embeddings using OpenAI
3. Store in Databricks Vector Search
4. Implement RAG query function
5. Test with 5 sample queries

**Solution Template**:
```python
# Step 1: Prepare documents
documents = [
    "Sales pipeline processes 1M records daily...",
    "Customer pipeline runs hourly...",
    # ... more documents
]

# Step 2: Generate embeddings
embeddings = OpenAIEmbeddings()
for doc in documents:
    doc["embedding"] = embeddings.embed_query(doc["text"])

# Step 3: Store in vector DB
vsc.upsert(endpoint_name="docs", index_name="pipeline-docs", inputs=documents)

# Step 4: RAG query
def rag_query(query: str):
    query_embedding = embeddings.embed_query(query)
    results = vsc.similarity_search(endpoint_name="docs", index_name="pipeline-docs", query_vector=query_embedding)
    context = "\n".join([r["text"] for r in results])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    return llm.generate(prompt)

# Step 5: Test
rag_query("What is the sales pipeline?")
```

#### Exercise 2: Build SQL Generator Agent

**Objective**: Build an agent that generates SQL from natural language

**Tasks**:
1. Create schema documentation
2. Build SQL generation function
3. Add validation
4. Execute SQL safely
5. Format response

#### Exercise 3: Build Pipeline Monitor Agent

**Objective**: Build an agent that monitors pipelines and explains failures

**Tasks**:
1. Collect pipeline logs
2. Detect failures
3. Use LLM to explain failures
4. Generate recommendations
5. Send alerts

---

## ✅ Best Practices Summary

**RAG:** Chunk size/overlap to fit embeddings; use metadata filters; tune top_k (often 3–5).

**LLMs:** **Temperature** low (0.2–0.3) for SQL/code/analysis; 0.7 for chat. Set **max_tokens** to control cost and length. Clear prompts + few-shot examples; validate outputs.

**Vector DBs:** Use embedding dimension that matches your model; monitor latency and index size.

---

## 🎯 Next Steps

Practice building:
- RAG systems
- Chatbots
- SQL generators
- Pipeline monitoring agents

**Study Time**: Spend 2-3 weeks on AI agents, build real projects!

---

## 📚 Additional Resources

- **LangChain Documentation**: https://python.langchain.com/
- **Databricks Vector Search**: https://docs.databricks.com/
- **OpenAI API**: https://platform.openai.com/docs/

---

**Keep Building! 🚀**
