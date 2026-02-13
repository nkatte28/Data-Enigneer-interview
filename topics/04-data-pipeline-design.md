# Topic 4: Data Pipeline Design and Implementation

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Describe a structured approach to designing and implementing data pipelines
- Gather requirements and choose between batch vs streaming
- Design pipeline layers (raw, cleansed, processed) and orchestration
- Apply error handling, monitoring, and data validation at each stage
- Choose target storage and file formats based on access patterns
- Apply scalability, testing, documentation, and maintenance best practices
- Map common tools and tech stack to pipeline components

---

## 📖 How to Approach Data Pipeline Design and Implementation

A data pipeline **transports, processes, and delivers data** from sources into analytic or operational systems. Designing it well means: clear requirements, the right processing model (batch vs streaming), defined layers, orchestration, error handling, monitoring, and the right technology choices.

---

### 1. Requirement Gathering

Begin by understanding the **full set of requirements** before choosing technologies or writing code.

**Data sources**
- What systems produce the data? (databases, APIs, files, event streams, CRM, ERP)
- Schema, volume per source, and update patterns (full refresh vs incremental)
- Access method (pull vs push), authentication, rate limits, and SLAs

**Volume and frequency**
- **Amount of data**: rows/events per day or per run; growth expectations
- **Frequency of processing**: real-time, every minute, hourly, daily, weekly
- **Latency requirement**: how fresh does the data need to be for the business?

**Business requirements**
- Who consumes the data and for what (reporting, ML, operational dashboards)?
- Required grain (e.g. one row per order, per day, per user)
- Key metrics, dimensions, and business rules (e.g. definitions of “active user”, “revenue”)

**Constraints and limits**
- Budget (infra, tools, licenses)
- Compliance (GDPR, PII, retention, audit)
- Existing tech stack, team skills, and organizational standards
- SLAs (availability, data freshness, recovery time)

**Batch vs streaming decision (based on frequency and latency)**

| If you need… | Prefer |
|--------------|--------|
| Low latency (seconds/minutes), continuous flow | **Streaming** (Kafka, Kinesis, Flink, Spark Streaming) |
| Periodic runs (hourly/daily), large bulk loads | **Batch** (scheduled jobs, Spark, SQL, scripts) |
| Both | **Lambda/Kappa** or batch + streaming with a unified serving layer |

Once requirements are clear, document them (source catalog, target schema, SLAs, owners) and use them to drive the rest of the design.

---

### 2. Architecture and Processing Model

**Choose the processing model**
- **Batch**: Extract on a schedule (e.g. nightly), transform in bulk, load to warehouse/lake. Good for large historical loads and non–real-time analytics.
- **Streaming**: Ingest events as they arrive, process in small windows or per event, write to DB/lake/API. Good for real-time dashboards, alerts, and event-driven apps.
- **Hybrid**: e.g. streaming for hot path, batch for backfill and reprocessing (Lambda-style).

**Design high-level flow**
- Sources → **ingestion** → **storage (raw)** → **processing/transformation** → **storage (curated)** → **serving** (warehouse, APIs, dashboards).
- Draw a simple diagram: systems, pipelines, and dependencies.

**Idempotency and reprocessing**
- Design so re-running a pipeline (or replaying events) does not duplicate or corrupt data (e.g. overwrite by partition, merge by key, dedupe by event id).

---

### 3. Pipeline Orchestration and Data Layers

**Orchestration tool**
- Use a workflow orchestrator to **schedule**, **trigger**, and **monitor** jobs and to manage dependencies and retries.
- Examples: **Apache Airflow**, **Dagster**, **Prefect**, **Control-M**, **Autosys**, **Azure Data Factory**, **AWS Step Functions**, **Databricks Workflows**.

**Data layers (medallion or similar)**

Define where data lives at each stage and for how long.

| Layer | Purpose | Retention | Notes |
|-------|---------|-----------|--------|
| **Raw / landing** | Immutable copy of source data | Per policy (e.g. 30–90 days) | Schema-on-read; minimal or no transformation |
| **Cleansed / sanitized** | Cleaned, validated, deduplicated | As needed for reprocessing | Data quality checks; reject bad records to a **reject/quarantine** area |
| **Processed / curated** | Business logic applied, aggregated, modeled | Long-term | Ready for analytics, ML, or reporting |

**Raw layer**
- **Do you need raw stored?** Usually yes for audit, reprocessing, and debugging.
- **Retention**: Define retention (e.g. 90 days) and lifecycle (e.g. move to cold storage or delete).
- **Format**: Often columnar (Parquet/ORC) or event format (Avro) for efficiency.

**Cleansed / sanitized layer**
- **Preprocessing**: Parsing, type coercion, null handling, deduplication.
- **Data quality validations**: Schema conformance, null checks, range checks, referential integrity, business rules.
- **Reject layer**: Rows that fail validation go to a **reject/quarantine** table or path (with reason and timestamp) for review and optional reprocessing. Define which validations cause a reject (e.g. invalid dates, missing keys).

**Processing / transformation layer**
- **Business logic**: Calculations, aggregations, windowing, joins.
- **Transformations**: Mapping source → target schema; applying business rules (e.g. currency conversion, segment derivation).
- **Enrichment**: Lookups (dimensions, reference data), external APIs (with caching/rate limits).
- Keep logic in version-controlled code (SQL, Python, Spark) and, where possible, reusable components or templates.

**Orchestration and dependencies**
- Model DAGs so that: raw → cleansed → processed → load run in order; parallelize where independent.
- Use orchestration for retries, backfill, and SLA-based alerting.

---

### 4. Error Handling and Monitoring

**Error handling**
- **Fail fast**: When data or configuration is invalid, fail the job with a clear error and stack trace so bad data does not propagate ([ref](https://www.kdnuggets.com/the-complete-guide-to-building-data-pipelines-that-dont-break)).
- **Validation at boundaries**: At each stage (ingest, cleanse, transform, load), validate schema and critical invariants before writing downstream.
- **Retries**: Configure retries for transient failures (network, throttling); use exponential backoff and max attempts.
- **Dead letter / reject path**: Send bad records to a reject store with error reason and payload for debugging and optional replay.
- **Logging**: Structured logs (JSON) with job_id, run_id, stage, row counts, and error details for troubleshooting.

**Monitoring and alerting**
- **Instrumentation**: Emit metrics (records in/out, latency, failure flags) and logs from each job ([ref](https://www.prefect.io/blog/data-pipeline-monitoring-best-practices)).
- **Collection**: Use agents or APIs to collect logs and metrics into a central system (e.g. CloudWatch, Datadog, Prometheus).
- **Observability**: Dashboards for throughput, latency, failure rates, and data freshness per pipeline and per table.
- **Alerting**: Thresholds on failure rate, latency, row count drops, or schema changes; route to on-call or Slack/email.
- **Health checks**: Regular checks that “data gets in, data gets built, and data gets out” ([ref](https://www.palantir.com/docs/foundry/maintaining-pipelines/recommended-health-checks))—e.g. source availability, intermediate table freshness, target completeness.

**Risks of weak monitoring**
- Data quality issues, latency spikes, undetected failures, and compliance or SLA breaches ([ref](https://towardsdev.com/end-to-end-data-pipeline-monitoring-ensuring-accuracy-latency-f53794d0aa78)).

---

### 5. Target Loading

**Destination**
- **Warehouse** (Snowflake, Redshift, BigQuery): for SQL analytics, BI, and reporting.
- **Data lake / lakehouse** (S3, ADLS, Delta Lake, Iceberg): for large-scale, multi-format, and ML workloads.
- **Databases / APIs**: for operational use cases or real-time serving.

**File format and layout (for lake/lakehouse)**
- **Frequently accessed, analytical**: Prefer **columnar** (e.g. **Parquet**, **ORC**) for query performance and compression.
- **Archival / cold**: Same formats with lifecycle policies (e.g. move to cheaper storage); avoid heavy compression if rarely read.
- **Partitioning**: By date, tenant, or key dimension to enable partition pruning and efficient overwrites.

**Load strategy**
- **Full refresh**: Replace entire table/partition (e.g. small dimensions).
- **Incremental / merge**: Append or upsert by key (e.g. event streams, CDC); use partition overwrite or merge to keep idempotency.

**Scheduling**
- Align with **frequency** from requirements (hourly, daily, etc.) and **dependencies** (e.g. source export, upstream pipelines).
- Use the orchestrator for schedule, concurrency limits, and SLA-based monitoring.

---

### 6. Data Validation and Testing

**Data quality dimensions** ([ref](https://dagster.io/blog/how-to-enforce-data-quality-at-every-stage))
- **Timeliness**: Data is fresh and within SLA.
- **Completeness**: No missing partitions or unexpected drop in row counts.
- **Accuracy**: Values match expectations (ranges, formats, cross-checks).
- **Schema conformance**: Column types and nullability match contract.
- **Consistency**: Align with source or other systems where required.

**Where to validate**
- At **ingest**: schema and basic sanity checks.
- After **cleanse**: business rules and reject routing.
- After **transform**: row counts, key metrics, and sample checks.
- At **load**: target row counts and freshness.

**Testing types**
- **Unit tests**: Test individual functions or steps (e.g. a transformation or a validation rule) in isolation with fixed inputs and expected outputs.
- **Integration tests**: Run a small end-to-end path (e.g. raw → cleansed → one table) in a test environment.
- **Regression tests**: After code changes, run the same suite to ensure existing behavior is not broken (e.g. same inputs produce same outputs).
- **Data quality tests**: Assertions on freshness, row counts, nulls, and key metrics (e.g. Great Expectations, dbt tests, custom checks).

Implement checks as part of the pipeline or as separate orchestrated steps that fail the run when assertions fail.

---

### 7. Scalability and Performance Optimization

**Design for growth**
- Anticipate **data volume** and **concurrency** (more sources, more consumers, more frequent runs).
- Prefer **horizontal scaling**: add workers or partitions rather than bigger single nodes.

**Technology choices**
- **Distributed processing**: e.g. **Apache Spark** for batch and micro-batch; **Flink** or **Kafka Streams** for streaming.
- **Cloud and serverless**: Use managed services (Lambda, Glue, Dataflow, EMR, Databricks) for elasticity and less ops.

**Optimization**
- **Partitioning** and **clustering** in warehouse and lake for partition pruning and faster scans.
- **Incremental processing** where possible (only new/changed data) instead of full scans.
- **Resource tuning**: memory, parallelism, and shuffle to avoid OOM and skew.
- **Cost**: Right-size clusters and storage; use spot/preemptible where appropriate.

---

### 8. Documentation and Knowledge Sharing

- **Pipeline catalog**: What pipelines exist; sources, targets, schedule, and owner.
- **Data dictionary**: Meaning of key tables and columns; business definitions.
- **Runbooks**: How to trigger, backfill, and troubleshoot; where logs and metrics live; escalation path.
- **Architecture diagrams**: End-to-end flow and integration points.
- **Change process**: How to add new sources, change logic, or extend retention; review and rollout steps.

Keep docs close to code (e.g. README in repo, comments for complex logic) and update them when the pipeline or requirements change.

---

### 9. Continuous Monitoring and Maintenance

- **Ongoing monitoring**: Review dashboards and alerts; tune thresholds as usage changes.
- **Incident response**: Clear ownership and playbooks for failures and data issues.
- **Backfills and reprocessing**: Document how to safely re-run or backfill after fixes or schema changes.
- **Lifecycle**: Retire or refactor pipelines when sources or requirements change; keep dependencies and libraries updated.
- **Reviews**: Periodic review of SLAs, cost, and quality with stakeholders.

---

## 🛠 Tools and Tech Stack (Reference)

### Batch pipelines

| Component | Examples |
|-----------|----------|
| **Extraction** | Custom scripts (Python, SQL), Fivetran, Airbyte, Stitch, JDBC/ODBC connectors |
| **Transformation** | **Spark (PySpark/Scala)**, **dbt**, **SQL** (warehouse-native), Pandas (small data) |
| **Loading** | **Data warehouses**: Redshift, Snowflake, BigQuery; **Data lakes**: S3, ADLS, HDFS; **Lakehouse**: Delta Lake, Iceberg |
| **Orchestration / scheduling** | **Airflow**, **Dagster**, **Prefect**, Control-M, Autosys, AWS Step Functions, Azure Data Factory, Databricks Workflows |
| **File formats (lake)** | **Parquet**, **ORC** for analytical tables; Avro for events; CSV/JSON for exchange |

### Streaming pipelines

| Component | Examples |
|-----------|----------|
| **Ingestion** | **Kafka**, **Kinesis**, **Pub/Sub**, Event Hub |
| **Processing** | **Flink**, **Spark Streaming**, **Kafka Streams**, ksqlDB, Databricks Structured Streaming |
| **Sinking** | Same warehouses/lakes as batch; also DBs, caches, APIs |

### Data quality and validation

| Need | Examples |
|------|----------|
| **Assertions and tests** | **Great Expectations**, **dbt tests**, custom Spark/SQL checks |
| **Monitoring / observability** | Datadog, CloudWatch, Prometheus, Grafana, pipeline-native UIs (Airflow, Dagster, Prefect) |

---

## 📋 Interview Cheat Sheet: “How do you approach pipeline design?”

1. **Requirements**: Sources, volume, frequency, latency, business rules, constraints → then **batch vs streaming**.
2. **Architecture**: High-level flow; idempotency; raw → cleansed → processed layers and retention.
3. **Orchestration**: Tool choice; DAG design; scheduling and dependencies.
4. **Layers**: Raw (retention), cleansed (validation, reject layer), processed (business logic, enrichment).
5. **Errors & monitoring**: Fail fast, validate at boundaries, retries, dead letter; metrics, logs, alerts, health checks.
6. **Target**: Warehouse vs lake; format (Parquet/ORC) and partitioning; load strategy and schedule.
7. **Quality & testing**: Unit, integration, regression, and data quality checks at each stage.
8. **Scalability**: Horizontal scaling, distributed engines, partitioning, incremental processing.
9. **Docs & maintenance**: Catalog, runbooks, monitoring, and continuous improvement.

---

## 📚 Additional Resources

- [ETL Pipelines: 5 Key Components and 5 Critical Best Practices](https://dagster.io/guides/etl/etl-pipelines-5-key-components-and-5-critical-best-practices)
- [Data Pipeline Monitoring: Best Practices for Full Observability](https://www.prefect.io/blog/data-pipeline-monitoring-best-practices)
- [How to Enforce Data Quality at Every Stage](https://dagster.io/blog/how-to-enforce-data-quality-at-every-stage)
- [Data Pipeline Orchestration (Databricks)](https://www.databricks.com/resources/whitepaper/data-pipeline-orchestration)
- [Google Dataflow pipeline best practices](https://cloud.google.com/dataflow/docs/guides/pipeline-best-practices)
