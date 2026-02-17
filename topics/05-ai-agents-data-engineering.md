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

By the end of this topic, you should be able to:
- Understand AI agents and their architecture
- Master LLM fundamentals and prompt engineering
- Build RAG systems with vector databases
- Create chatbots for data engineering
- Build AI agents for data pipeline automation
- Deploy AI agents in production
- Monitor and optimize AI systems
- Design scalable AI agent architectures

---

## 📖 Core Concepts

### 1. AI Agents Overview

**What is an AI Agent?**
An AI agent is an autonomous system that can perceive its environment, make decisions, and take actions to achieve specific goals using AI/ML models.

**Key Components**:
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

**Types of AI Agents**:

1. **Simple Agents**: Single-turn conversations
2. **Conversational Agents**: Multi-turn with memory
3. **Tool-Using Agents**: Can execute code, query databases
4. **Autonomous Agents**: Can plan and execute multi-step tasks

**Data Engineering Use Cases**:
- ✅ **Data Pipeline Chatbot**: Answer questions about pipelines
- ✅ **SQL Query Generator**: Generate SQL from natural language
- ✅ **Data Quality Monitor**: Detect and explain data issues
- ✅ **Documentation Assistant**: Auto-generate pipeline docs
- ✅ **Anomaly Detection**: Explain anomalies in data

---

### 2. Understanding Your Data: Sample Raw Data

**Before we build AI agents, let's see what we're working with!**

**Sample Sales Data**:
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

**Sample Pipeline Metadata**:
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

**What We're Trying to Achieve**:
1. Build AI agent that understands data pipelines
2. Answer questions about data
3. Generate SQL queries
4. Explain data quality issues
5. Automate data engineering tasks

---

### 3. LLM Fundamentals

**What is an LLM?**
Large Language Model - AI model trained on vast text data to understand and generate human-like text.

**Popular LLMs**:
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

**What is Prompt Engineering?**
The art of crafting effective prompts to get desired outputs from LLMs.

**Prompt Structure**:
```
System Message (Role/Context)
    ↓
User Query
    ↓
Context/Examples
    ↓
Output Format
```

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

**Chain-of-Thought Prompting**:
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

**Install Libraries**:
```python
# Install required packages
%pip install openai langchain databricks-vectorsearch
```

**OpenAI Integration**:
```python
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Simple completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a data engineering assistant."},
        {"role": "user", "content": "What is a data pipeline?"}
    ],
    temperature=0.7,
    max_tokens=500
)

answer = response.choices[0].message.content
print(answer)
```

**Databricks Foundation Models**:
```python
from databricks import sql
from langchain.llms import Databricks

# Use Databricks foundation models
llm = Databricks(
    endpoint_name="databricks-dbrx-instruct",
    model_kwargs={"temperature": 0.7}
)

response = llm("What is a data pipeline?")
print(response)
```

**LangChain Integration**:
```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Initialize LangChain LLM
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7
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

**What is a Vector Database?**
Specialized database for storing and searching high-dimensional vectors (embeddings).

**Why Vector Databases?**
- ✅ Fast similarity search
- ✅ Semantic search (meaning, not keywords)
- ✅ Handles high-dimensional vectors
- ✅ Optimized for ML workloads

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

**What is Databricks Vector Search?**
Managed vector database service in Databricks for storing and searching embeddings.

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

# Create index
index_name = "pipeline-docs-index"
vsc.create_index(
    endpoint_name=endpoint_name,
    index_name=index_name,
    primary_key="doc_id",
    index_schema={
        "fields": [
            {"name": "doc_id", "type": "string"},
            {"name": "text", "type": "string"},
            {"name": "embedding", "type": "vector", "dimension": 1536}
        ]
    }
)
```

**Generate Embeddings**:
```python
from langchain.embeddings import OpenAIEmbeddings

# Initialize embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Generate embedding for document
doc_text = "Sales pipeline processes 1M records daily from S3 to Redshift"
doc_embedding = embeddings.embed_query(doc_text)

print(f"Embedding dimension: {len(doc_embedding)}")
# Output: 1536
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

# Search
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

**What is RAG?**
Technique that combines retrieval (finding relevant documents) with generation (LLM creating response).

**Why RAG?**
- ✅ Reduces hallucinations (LLM makes up facts)
- ✅ Uses up-to-date information
- ✅ Grounds responses in real data
- ✅ Better for domain-specific knowledge

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

**Step 2: Generate Embeddings**:
```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Split documents into chunks
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

**Step 4: RAG Query Function**:
```python
def rag_query(user_query: str, top_k: int = 3):
    """
    RAG query: Retrieve relevant context and generate response
    """
    # Step 1: Generate query embedding
    query_embedding = embeddings.embed_query(user_query)
    
    # Step 2: Search similar documents
    results = vsc.similarity_search(
        endpoint_name=endpoint_name,
        index_name=index_name,
        query_vector=query_embedding,
        num_results=top_k
    )
    
    # Step 3: Build context
    context = "\n\n".join([r["text"] for r in results])
    
    # Step 4: Build prompt
    prompt = f"""You are a data engineering assistant. Answer questions using the provided context.

Context:
{context}

Question: {user_query}

Answer based on the context above. If the answer is not in the context, say "I don't have that information."
"""
    
    # Step 5: Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful data engineering assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Example usage
answer = rag_query("What is the status of sales pipeline?")
print(answer)
```

**Step 5: Enhanced RAG with Metadata Filtering**:
```python
def rag_query_with_filter(user_query: str, pipeline_name: str = None):
    """
    RAG query with metadata filtering
    """
    query_embedding = embeddings.embed_query(user_query)
    
    # Search with metadata filter
    results = vsc.similarity_search(
        endpoint_name=endpoint_name,
        index_name=index_name,
        query_vector=query_embedding,
        num_results=3,
        filters={"pipeline": pipeline_name} if pipeline_name else None
    )
    
    context = "\n\n".join([r["text"] for r in results])
    
    prompt = f"""Context:
{context}

Question: {user_query}

Answer:
"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

---

### 6. Databricks ML & AI

**Databricks AI Features**:
- ✅ **MLflow**: Model tracking and deployment
- ✅ **Vector Search**: Managed vector database
- ✅ **Foundation Models**: Pre-trained LLMs
- ✅ **ML Runtime**: Pre-configured ML environments

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

**Databricks Foundation Models**:
```python
from langchain.llms import Databricks

# Use Databricks DBRX model
llm = Databricks(
    endpoint_name="databricks-dbrx-instruct",
    model_kwargs={"temperature": 0.7, "max_tokens": 500}
)

response = llm("What is a data pipeline?")
print(response)
```

---

### 7. Building Chatbots

**What is a Chatbot?**
Conversational AI agent that can interact with users in natural language.

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

# Initialize LLM
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
    
    # Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
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

**What are Data Engineering AI Agents?**
Specialized AI agents for automating data engineering tasks.

**Use Cases**:
1. **SQL Query Generator**: Generate SQL from natural language
2. **Pipeline Monitor**: Monitor and explain pipeline failures
3. **Data Quality Agent**: Detect and explain data issues
4. **Documentation Generator**: Auto-generate pipeline docs
5. **Anomaly Explainer**: Explain data anomalies

#### 8.1 SQL Query Generator Agent

**Agent that Generates SQL from Natural Language**:
```python
def sql_generator_agent(user_query: str, schema_info: str) -> str:
    """
    Generate SQL query from natural language
    """
    prompt = f"""You are a SQL query generator. Generate SQL queries from natural language.

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
        temperature=0.3  # Lower temperature for more deterministic SQL
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
            temperature=0.7
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
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Example usage
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
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Example usage
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

**Real-Time Use Cases**:
1. **Streaming Data Analysis**: Analyze streaming data in real-time
2. **Anomaly Detection**: Detect and explain anomalies
3. **Real-Time Recommendations**: Provide recommendations based on live data
4. **Alert Explanation**: Explain alerts in real-time

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
            temperature=0.7
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
        temperature=0.3
    )
    
    analysis = response.choices[0].message.content
    
    return {
        "is_anomaly": "Yes" in analysis,
        "explanation": analysis
    }

# Example usage
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

**What is Fine-Tuning?**
Training a pre-trained LLM on domain-specific data to improve performance.

**When to Fine-Tune**:
- ✅ Domain-specific terminology
- ✅ Specific output format
- ✅ Better accuracy needed
- ✅ Cost optimization (smaller model)

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
        "n_epochs": 3,
        "learning_rate_multiplier": 1.0
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

**Deploying AI Agents in Production**:

**1. Model Serving with MLflow**:
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

**Monitoring AI Agents**:
```python
import mlflow

# Log metrics
mlflow.log_metric("response_time", 1.2)
mlflow.log_metric("token_usage", 500)
mlflow.log_metric("user_satisfaction", 4.5)

# Log prompts and responses
mlflow.log_text(prompt, "prompt.txt")
mlflow.log_text(response, "response.txt")
```

**Cost Optimization**:
- ✅ Use smaller models when possible
- ✅ Cache common queries
- ✅ Limit token usage
- ✅ Use fine-tuned models

---

### 13. AI Agents Interview Questions & Answers

#### Q1: Explain RAG Architecture

**Question**: "Explain how RAG (Retrieval Augmented Generation) works. Walk me through the architecture."

**Answer Structure**:

**1. What is RAG?**
RAG combines retrieval (finding relevant documents) with generation (LLM creating response).

**2. RAG Flow**:
```
User Query → Embed Query → Vector Search → Retrieve Context → Build Prompt → LLM Generation → Response
```

**3. Key Components**:
- **Embedding Model**: Converts text to vectors
- **Vector Database**: Stores and searches embeddings
- **Retriever**: Finds relevant documents
- **LLM**: Generates response using context

**4. Why RAG?**
- ✅ Reduces hallucinations
- ✅ Uses up-to-date information
- ✅ Better for domain-specific knowledge

**Key Points**:
- ✅ RAG = Retrieval + Generation
- ✅ Vector search finds relevant context
- ✅ LLM uses context to generate accurate responses

---

#### Q2: How Do You Choose a Vector Database?

**Question**: "How do you choose between different vector databases? What factors matter?"

**Answer Structure**:

**1. Vector Database Options**:
- **Databricks Vector Search**: Managed, integrated
- **Pinecone**: Fully managed, easy to use
- **Chroma**: Open-source, self-hosted
- **Weaviate**: Open-source, feature-rich

**2. Decision Factors**:

**Managed vs Self-Hosted**:
- Managed: Easier, but less control
- Self-hosted: More control, but more maintenance

**Scalability**:
- How many vectors?
- Query throughput?
- Growth rate?

**Integration**:
- Works with existing stack?
- Databricks integration?
- API compatibility?

**3. Recommendation**:
- **Databricks users**: Use Databricks Vector Search
- **Quick start**: Use Pinecone
- **Cost-sensitive**: Use Chroma (self-hosted)

**Key Points**:
- ✅ Consider managed vs self-hosted
- ✅ Evaluate scalability needs
- ✅ Check integration with existing tools

---

### 14. System Design with AI Agents

**Design: Data Engineering Chatbot**:
```
User → API Gateway → Lambda → RAG System → Vector DB → LLM → Response
```

**Components**:
- **API Gateway**: Handle requests
- **Lambda**: Orchestrate agent
- **RAG System**: Retrieve context
- **Vector DB**: Store embeddings
- **LLM**: Generate responses

---

### 15. Hands-On Exercises

#### Exercise 1: Build Simple RAG System

**Objective**: Build a basic RAG system

**Tasks**:
1. Prepare documents
2. Generate embeddings
3. Store in vector database
4. Implement RAG query
5. Test with sample queries

---

## ✅ Best Practices Summary

### RAG
- ✅ Chunk documents appropriately
- ✅ Use good embedding models
- ✅ Filter by metadata when possible
- ✅ Retrieve top-K relevant documents

### LLMs
- ✅ Use appropriate temperature
- ✅ Provide clear prompts
- ✅ Use few-shot examples
- ✅ Validate outputs

### Vector Databases
- ✅ Choose right dimension
- ✅ Index appropriately
- ✅ Monitor performance
- ✅ Update embeddings regularly

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
