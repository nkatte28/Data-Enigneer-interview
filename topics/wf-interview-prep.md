## Wells Fargo (WF) – GenAI / Data Engineering Interview Prep

### 🔗 Quick Links

- [1. Role Positioning (WF + Nike Experience)](#1-role-positioning-wf--nike-experience)
- [2. Python for Data Engineering](#2-python-for-data-engineering)
- [3. SQL & Data Processing](#3-sql--data-processing)
- [4. Generative AI & LLMs](#4-generative-ai--llms)
- [5. CI/CD, GitHub, GitHub Actions](#5-cicd-github-github-actions)
- [6. Workflow Orchestration (Airflow)](#6-workflow-orchestration-airflow)
- [7. Short “Tell Me About X” Stories](#7-short-tell-me-about-x-stories)

---

### 1. Role Positioning (WF + Nike Experience)

**How to position yourself for WF:**

- **Core**: Python + SQL + data processing.
- **Differentiator**: Hands-on **LLMs, Databricks, vector search, RAG, dev-productivity automation**.
- **Deployment**: CI/CD, GitHub Actions/Jenkins, productionized agents and services.
- **Orchestration**: Airflow for reliable workflows.

**Sample “Tell me about yourself” (WF context)**:

> I’m a data engineer with strong Python and SQL experience, and in my most recent role at Nike I focused heavily on applying Generative AI to data engineering problems. I built a GenAI-powered documentation automation framework integrated into CI/CD, where a post-deploy Jenkins stage extracted PySpark DAGs, YAML configs, and DDLs from Git and auto-published production-aligned architecture docs to Confluence, cutting manual documentation by about 70%. I also built a semantic documentation engine on Databricks using a hosted LLaMA model plus structured prompts to analyze Spark transformations and dependency graphs, saving ~15–20 engineering hours per sprint. Recently I’ve been integrating tools like Cursor, MCP, and Confluence to give developers in-IDE conversational access to live architecture artifacts, reducing context switching and speeding onboarding. I’d like to bring that blend of solid data engineering and GenAI automation to Wells Fargo’s data and risk platforms.

---

### 2. Python for Data Engineering

**Common questions**:

1. How do you process large files in Python efficiently?
2. How do you structure reusable data pipeline code?
3. How do you handle errors and logging in ETL jobs?

**Key points**:

- Stream / iterate over data (don’t load everything into memory).
- Encapsulate logic into functions/classes for reuse and testing.
- Use `logging`, not `print`, and surface failures clearly.

**Simple example – streaming CSV and basic transform**:

```python
import csv
from typing import Iterator, Dict

def read_sales(path: str) -> Iterator[Dict[str, str]]:
    with open(path, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row  # stream row by row

def transform_sale(row: Dict[str, str]) -> Dict[str, str]:
    amount = float(row["amount"])
    row["amount_usd"] = f"{amount:.2f}"
    return row

def process_sales(input_path: str, output_path: str) -> None:
    with open(output_path, mode="w", newline="") as f_out:
        writer = None
        for row in read_sales(input_path):
            out_row = transform_sale(row)
            if writer is None:
                writer = csv.DictWriter(f_out, fieldnames=out_row.keys())
                writer.writeheader()
            writer.writerow(out_row)
```

**How to explain**:

- `read_sales` streams input line by line → works for large files.
- `transform_sale` isolates transformation → unit-testable.
- Easy to drop this into Airflow or a CI step.

---

### 3. SQL & Data Processing

**Common questions**:

1. Write a query for daily revenue by customer.
2. How do you handle slowly changing dimensions (SCD)?
3. How would you debug a data quality issue (e.g., negative amounts)?

**Daily revenue by customer**:

```sql
SELECT
    customer_id,
    sale_date,
    SUM(amount) AS daily_revenue
FROM sales
WHERE sale_date BETWEEN DATE '2024-01-01' AND DATE '2024-01-31'
GROUP BY customer_id, sale_date
ORDER BY sale_date, customer_id;
```

**Identify suspicious (negative) sales**:

```sql
SELECT
    sale_id,
    customer_id,
    amount,
    sale_date
FROM sales
WHERE amount < 0;
```

**How to explain**:

- Mention joins, window functions, CTEs, and aggregations as standard tools.
- Connect to GenAI work: you used such queries as inputs for LLM-based documentation or anomaly explanations.

---

### 4. Generative AI & LLMs

**Goal of this section**: Be a **code-first cheat sheet** for using OpenAI / Databricks LLaMA / LangChain – what functions you actually call, what the key params mean, and how they fit together.

**Core concepts**:

- **Embedding**: Map text → vector; similar text → nearby vectors.
- **Vector DB**: Store these vectors for semantic search.
- **RAG**: Retrieve relevant docs from vector DB, then let LLM answer using that context.
- **Temperature**: 0–0.3 for deterministic SQL/analysis; ~0.7 for chat/explanations.

#### 4.1 OpenAI – core API calls (Python)

**Chat completion (GPT-4)**:

```python
from openai import OpenAI

client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful data engineering assistant."},
        {"role": "user", "content": "Explain what a data pipeline is in 3 sentences."}
    ],
    temperature=0.5,   # 0.0–0.3 strict; 0.5 balanced; 0.7+ creative
    max_tokens=200     # hard cap on reply length
)

answer = resp.choices[0].message.content
```

**Embeddings (for vector search / RAG)**:

```python
from openai import OpenAI

client = OpenAI()

text = "Sales pipeline processes 1M records daily from S3 to Delta."
emb = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
).data[0].embedding  # list[float], length = model dimension (e.g. 1536)
```

Key points they may quiz you on:

- `temperature`, `max_tokens`, and `top_p` control **randomness** and **length**.
- Embeddings are just **vectors**; you always pair them with a **vector index** (FAISS, Chroma, Databricks Vector Search, etc.).

**Simple “RAG-like” helper**:

```python
from openai import OpenAI

client = OpenAI()

def answer_with_context(question: str, context: str) -> str:
    prompt = f"""You are a data engineering assistant.
Use ONLY the context below to answer the question.

Context:
{context}

Question: {question}

If the answer is not in the context, say "I don't have that information."
"""
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,   # low: more factual and repeatable
        max_tokens=400
    )
    return resp.choices[0].message.content
```

**How to connect to your Nike project**:

- You generalized this pattern into a **semantic documentation engine** on Databricks (LLaMA model).
- Inputs: Spark DAGs, YAML configs, DDLs, dependency graphs, schema metadata.
- Outputs: Architecture narratives, data-flow diagrams, table-level documentation.
- Impact: ~15–20 engineering hours saved per sprint.

**Common GenAI questions**:

- How do you reduce hallucinations?
  - Use RAG, constrain prompts (“if not in context, say you don’t know”), and sometimes post-validation.
- How did you integrate LLMs into existing platforms?
  - Databricks-hosted LLaMA, CI post-deploy stages, Confluence API, etc.

#### 4.2 LangChain essentials (WF-relevant)

**Core pieces**:

- `ChatOpenAI` / `ChatAnthropic`: wrap chat models (you already know how to tune `temperature`, `max_tokens`).
- `PromptTemplate`: parameterized prompts.
- `VectorStore` + `Retriever`: encapsulate semantic search for RAG.
- `ConversationalRetrievalChain`: very common for chatbot-style Q&A over docs.

**Tiny example – LangChain QA over in-memory docs**:

```python
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain

docs = [
    "Sales pipeline (sales_etl) processes 1M records daily at 2 AM.",
    "Customer pipeline (customer_etl) runs hourly and loads data into Delta."
]

emb = OpenAIEmbeddings()
store = FAISS.from_texts(docs, embedding=emb)

llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)  # low temp for factual answers

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=store.as_retriever(search_kwargs={"k": 2})
)

chat_history = []
result = qa({"question": "When does the sales pipeline run?", "chat_history": chat_history})
print(result["answer"])
```

**Quick LangChain interview checks**:

- When would you use a `Retriever` vs calling the vector store directly?
- How do you control cost/latency in LangChain chains (e.g., fewer docs in retriever, smaller models, caching)?
- How would you log prompts and responses (for monitoring and safety)?

#### 4.3 Building LLM apps on Databricks (LLaMA) with LangChain

Assume you have a Databricks **model serving endpoint** exposing a LLaMA-like chat model (e.g. `llama-doc-assistant`).

**LangChain LLM wrapper (Databricks endpoint)**:

```python
from langchain.llms import Databricks

llm = Databricks(
    endpoint_name="llama-doc-assistant",
    model_kwargs={
        "temperature": 0.2,   # deterministic for analysis/docs
        "max_tokens": 800
    },
)
```

**Strict prompt for architecture documentation**:

```python
from textwrap import dedent

def build_arch_prompt(dag_text: str, yaml_text: str, ddl_text: str) -> str:
    return dedent(f"""
    You are a senior data platform architect.

    INPUT ARTIFACTS:
    - DAG definition (PySpark / Airflow): 
    {dag_text}

    - Workflow YAML:
    {yaml_text}

    - Table DDL / schema:
    {ddl_text}

    TASK:
    1. Describe the end-to-end data flow (source → transforms → targets).
    2. List the main datasets and their purposes.
    3. Highlight any data quality / lineage considerations.

    HARD RULES:
    - Only use information from the input artifacts.
    - If something is not specified, say "Not specified in artifacts."
    - Output must be in Markdown with the following sections:
      ## Overview
      ## Data Flow
      ## Tables and Schemas
      ## Data Quality and Lineage
    """).strip()
```

**Call Databricks LLaMA via LangChain**:

```python
def generate_arch_doc(dag_text: str, yaml_text: str, ddl_text: str) -> str:
    prompt = build_arch_prompt(dag_text, yaml_text, ddl_text)
    return llm(prompt)  # returns Markdown string
```

This mirrors what you actually did: strict prompt, deterministic temperature, clear output format.

#### 4.4 End-to-end: Jenkins → LLM → Confluence → Vector DB → Chatbot

**1. Jenkins stage calling a Python script**

```groovy
pipeline {
    agent any
    stages {
        stage('Tests') {
            steps {
                sh 'pytest'
            }
        }
        stage('Generate & Publish Docs') {
            environment {
                DATABRICKS_TOKEN = credentials('db-token')
                CONFLUENCE_USER = credentials('conf-user')
                CONFLUENCE_TOKEN = credentials('conf-token')
            }
            steps {
                sh 'python scripts/gen_arch_docs.py'
            }
        }
    }
}
```

**Key points**:

- Secrets come from Jenkins credentials.
- `gen_arch_docs.py` does: **load artifacts → call LLM → publish to Confluence → update vector DB**.

**2. Python script – artifacts → LLM → Confluence**

```python
import os
import requests
from langchain.llms import Databricks

llm = Databricks(endpoint_name="llama-doc-assistant")

def load_artifacts() -> tuple[str, str, str]:
    dag_text = open("dags/sales_etl.py").read()
    yaml_text = open("workflows/sales_etl.yaml").read()
    ddl_text = open("ddl/sales_tables.sql").read()
    return dag_text, yaml_text, ddl_text

def publish_to_confluence(space_key: str, title: str, body_markdown: str) -> str:
    base_url = os.environ["CONFLUENCE_BASE_URL"]
    user = os.environ["CONFLUENCE_USER"]
    token = os.environ["CONFLUENCE_TOKEN"]

    url = f"{base_url}/rest/api/content"
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": body_markdown,
                "representation": "wiki"  # or "storage" depending on Confluence setup
            }
        }
    }
    resp = requests.post(url, json=payload, auth=(user, token))
    resp.raise_for_status()
    page_id = resp.json()["id"]
    return page_id

def main():
    dag_text, yaml_text, ddl_text = load_artifacts()
    doc_md = generate_arch_doc(dag_text, yaml_text, ddl_text)  # from previous section

    page_id = publish_to_confluence(
        space_key="DATA",
        title="Sales ETL – Architecture Doc",
        body_markdown=doc_md,
    )
    print(f"Published Confluence page {page_id}")

    # After publish, we can send the same doc into a vector DB (next section)

if __name__ == "__main__":
    main()
```

**3. After publish: tokenize, embed, and store in a vector DB**

For interview simplicity, show Chroma/FAISS; in your real project, this is Databricks Vector Search.

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

def index_doc(doc_id: str, title: str, body_md: str, store_path: str = "faiss_index"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_text(body_md)

    texts = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        texts.append(chunk)
        metadatas.append({"doc_id": doc_id, "title": title, "chunk": i})

    embeddings = OpenAIEmbeddings()
    store = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)

    store.save_local(store_path)
    return store
```

You can call `index_doc` from `main()` after successfully publishing to Confluence.

**4. Final chatbot over architecture docs**

```python
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain

def load_store(store_path: str = "faiss_index") -> FAISS:
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(store_path, embeddings)

def build_arch_chatbot() -> ConversationalRetrievalChain:
    store = load_store()
    retriever = store.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
    )
    return qa

def chat_loop():
    qa = build_arch_chatbot()
    history = []
    while True:
        q = input("Q: ").strip()
        if not q or q.lower() in {"exit", "quit"}:
            break
        result = qa({"question": q, "chat_history": history})
        print(f"A: {result['answer']}\n")
        history.append((q, result["answer"]))
```

How to explain in interview:

- Jenkins stage triggers on deploy → calls Python script.
- Python script:
  - Loads artifacts from Git,
  - Calls Databricks LLaMA endpoint (strict prompt, low temperature),
  - Publishes Markdown to Confluence,
  - Splits the same content into chunks, embeds, and stores into a vector DB.
- A separate service (or notebook) exposes a chatbot using LangChain `ConversationalRetrievalChain` over that vector store, so devs can query “What does the sales ETL do?” directly.

---

### 5. CI/CD, GitHub, GitHub Actions

You’ve already done this with Jenkins; at WF they may ask about GitHub Actions specifically.

**Example GitHub Actions workflow (tests + GenAI docs)**:

```yaml
name: ci-pipeline

on:
  push:
    branches: [ main ]

jobs:
  test-and-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: pytest

      - name: Generate docs with LLM
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python scripts/generate_docs.py
```

**How to explain**:

- Triggers on push to `main`.
- Runs **unit tests** and then a **GenAI doc generation** step.
- Secrets (API keys) are stored in **GitHub Secrets**.
- Map this back to your Jenkins-based post-deploy documentation framework.

**Typical question**:

- “Describe a CI/CD pipeline you built around LLMs or data pipelines.”

Answer with your Nike story and then mention how you’d **port that concept to GitHub Actions** at WF.

**Git – key points & quick questions**:

- Always mention: branching strategy (feature branches, PRs), code reviews, commit hygiene, tagging releases.
- Comfortable with: `clone`, `pull`, `push`, `branch`, `merge`, resolving basic conflicts.

Example interview questions:

- How do you handle a bad commit that already went to `main`?
- How do you keep long-lived feature branches in sync with `main`?
- How do you structure commits so it’s easy to debug production issues?

**Jenkins – quick summary & sample**:

- Jenkins = CI/CD server; uses jobs or pipelines (often scripted in Groovy).
- You extended Jenkins with a **post-deploy stage** that called LLMs and updated Confluence.

Very small declarative pipeline sketch:

```groovy
pipeline {
    agent any
    stages {
        stage('Build & Test') {
            steps {
                sh 'pytest'
            }
        }
        stage('Post-deploy Docs') {
            steps {
                sh 'python scripts/gen_arch_docs.py'
            }
        }
    }
}
```

Typical questions:

- How do you pass secrets (API keys) into Jenkins/GitHub Actions safely?
- Where would you put a GenAI doc step – before deploy (preview) or after deploy (source of truth)?
- How do you debug a failed pipeline stage?

---

### 6. Workflow Orchestration (Airflow)

**Simple explanation**:

- Airflow is an **orchestration** tool, not a compute engine.
- You define **DAGs** of tasks with explicit dependencies.
- Good for retries, alerts, SLAs, backfills.

**Basic Airflow DAG example**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extracting data from S3...")

def transform():
    print("Running PySpark job or SQL transforms...")

def load():
    print("Loading into Delta / warehouse...")

with DAG(
    dag_id="sales_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_load = PythonOperator(task_id="load", python_callable=load)

    t_extract >> t_transform >> t_load
```

**Extended Airflow example – operators, XCom, and explanation**:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

def extract(**context):
    rows = ["r1", "r2"]  # pretend we read from S3
    # Push to XCom so downstream tasks can pull it
    context["ti"].xcom_push(key="rows", value=rows)

def transform(**context):
    rows = context["ti"].xcom_pull(key="rows", task_ids="extract")
    cleaned = [r.upper() for r in rows]
    context["ti"].xcom_push(key="cleaned", value=cleaned)

def load(**context):
    cleaned = context["ti"].xcom_pull(key="cleaned", task_ids="transform")
    print(f"Loading {cleaned} into target table...")

with DAG(
    dag_id="sales_etl_xcom",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    t_extract = PythonOperator(
        task_id="extract",
        python_callable=extract,
        provide_context=True,
    )

    t_transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
        provide_context=True,
    )

    t_load = PythonOperator(
        task_id="load",
        python_callable=load,
        provide_context=True,
    )

    t_notify = BashOperator(
        task_id="notify",
        bash_command='echo "sales_etl_xcom completed successfully"'
    )

    t_extract >> t_transform >> t_load >> t_notify
```

How to explain:

- `PythonOperator` runs Python callables; `BashOperator` runs shell.
- `XCom` is used to pass **small pieces of data** between tasks (`xcom_push` / `xcom_pull`).
- Data flow: `extract` → `transform` → `load` → `notify`.

Quick Airflow interview questions:

- When would you use XCom vs writing to storage (S3, DB)?
- How do you handle retries and alerting for failing tasks?
- How do you manage Airflow connections and secrets?
- How would you document DAGs and make them discoverable (tie to your LLM docs story)?

**How to tie this to LLM work**:

- Your documentation engine can read DAG definitions and logs.
- LLM generates human-readable pipeline overviews and failure summaries.

---

### 7. Short “Tell Me About X” Stories

Use these as quick answers.

**Python**:

> I’ve built multiple data pipelines in Python, including streaming large CSV and JSON logs using iterators so we don’t blow up memory, and wrapping logic into reusable functions and modules. In my GenAI projects I used Python to orchestrate calls to Databricks-hosted LLaMA models, manage embeddings and vector indexes, and integrate with Confluence and Jenkins to automate documentation and developer workflows.

**SQL**:

> I’m comfortable with complex joins, window functions, CTEs, and aggregate queries. I’ve used SQL for daily and weekly revenue reports, cohort analysis, and for data quality checks like detecting negative or inconsistent values. Some of those queries fed directly into our GenAI documentation engine, where an LLM would explain what a pipeline or view does in clear business language.

**LLMs / GenAI**:

> The most impactful GenAI system I built was a documentation automation framework. After each deployment, a CI stage extracted PySpark DAGs, YAML workflow configs, and DDLs from Git. A Databricks-hosted LLaMA model with structured prompts generated architecture narratives and data-flow diagrams, which were auto-published to Confluence. That cut manual documentation work by about 70% and saved roughly 15–20 engineer-hours per sprint.

**CI/CD**:

> I treat data and ML systems like software: code in Git, automated tests, and pipelines that build, test, and deploy artifacts. In my last role I extended the pipeline with a post-deploy LLM stage that generated or updated documentation. At Wells Fargo I’d use a similar approach with GitHub Actions and the bank’s deployment platforms, making sure all GenAI steps are auditable and safe.

**Airflow / Orchestration**:

> I use orchestration tools like Airflow to model end-to-end ETL workflows: extract from sources, transform via Spark or SQL, and load into a warehouse or data lake. I rely on DAGs, retries, and alerting for reliability. A natural extension is letting an LLM consume DAG metadata and failure logs to generate human-readable explanations for on-call engineers and platform owners.

---

This doc is meant as a **fast revision sheet** for WF interviews: skim sections before the call, and reuse code snippets and stories as structured answers.


