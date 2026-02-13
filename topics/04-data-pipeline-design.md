# Topic 4: Data Pipeline Design and Implementation

## 🎯 Learning Goals

By the end of this topic, you should be able to:
- Describe a structured approach to designing and implementing data pipelines
- Gather requirements and choose between batch vs streaming
- Apply **pipeline design principles**: decoupling with storage, single responsibility, fault isolation, DAG design, schema/contracts, incremental vs full refresh
- Design pipeline layers (raw, cleansed, processed) and orchestration
- Apply error handling, monitoring, and data validation at each stage
- Choose target storage and file formats based on access patterns
- **Scale pipelines**: know what to scale (ingestion, compute, storage), horizontal vs vertical, partitioning, handling skew, autoscaling, and tuning
- Apply testing, documentation, and maintenance best practices
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

#### Pipeline Design Principles and Patterns

**Decouple stages with storage**
- Insert **persistent storage** (e.g. raw layer in object store or lake) between ingest and transform, and between transform and load. That way:
  - Ingestion can run independently of downstream; if transform fails, you don’t re-pull from source.
  - You can reprocess from raw without touching the source again.
- Avoid “tight chains” where one job calls the next in memory with no checkpoint in between.

**Single responsibility per job**
- Each pipeline or DAG task should do **one clear thing** (e.g. “ingest source A”, “cleanse table X”, “build aggregate Y”). That makes debugging, testing, and scaling easier.
- Split large pipelines into smaller, composable jobs that the orchestrator wires together.

**Fault isolation**
- A failure in one source or one partition should not block others. Use:
  - **Separate tasks** per source or per partition where it makes sense.
  - **Try/catch and reject paths** so bad data goes to quarantine and the rest continues.
- Design so that fixing one failed slice (e.g. one day’s partition) and re-running does not require a full pipeline run.

**DAG design**
- **Fan-out then fan-in**: Ingest multiple sources in parallel (fan-out), then join or merge in a later step (fan-in). Avoid one long sequential chain.
- **Clear dependencies**: Define task dependencies explicitly in the orchestrator; avoid hidden ordering that depends on execution order.
- **Idempotent tasks**: Each task should be safe to re-run (same inputs → same outputs; use partition overwrite or merge keys).
- **Bounded parallelism**: Use orchestrator concurrency limits so that too many parallel jobs don’t overload sources or the cluster.

**Schema and contract design**
- **Data contracts**: Agree on schema (column names, types, nullability) between producers and consumers; use schema registry or shared DDL where possible.
- **Schema evolution**: Prefer **additive** changes (new optional columns, new partitions); avoid breaking renames or type changes without a migration path.
- **Versioned outputs**: For critical datasets, consider versioning (e.g. by run date or version column) so consumers can pin to a known good version.

**Incremental vs full refresh**
- **Incremental**: Only process new or changed data (e.g. by `updated_at`, watermark, or CDC). Reduces cost and time; requires a reliable way to detect changes and idempotent merge/upsert.
- **Full refresh**: Reprocess everything. Simpler and correct by construction; use when data is small or when incremental logic is complex or unreliable.
- **Hybrid**: Full refresh for small dimensions; incremental for large fact tables or event streams.

**Backpressure and rate limiting**
- For **pull-based** ingestion (you query the source), respect rate limits and use backoff; consider batching or windowing to avoid overloading the source.
- For **push-based** (Kafka, Kinesis), scale consumers and partition count so that lag stays bounded; use dead-letter queues for poison messages.

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
- Anticipate **data volume** (rows/events per day, growth rate) and **concurrency** (more sources, more consumers, more frequent runs).
- Prefer **horizontal scaling** (add workers, partitions, or instances) over **vertical scaling** (bigger single nodes)—horizontal scales further and avoids single-point bottlenecks.
- Plan for **2–5x** growth in volume or frequency so the pipeline doesn’t need a rewrite when usage increases.

---

#### What to scale: ingestion, compute, storage

| Layer | What scales | How |
|-------|-------------|-----|
| **Ingestion** | Throughput (events/rows per second) | More connectors, more Kafka partitions / Kinesis shards, parallel pull jobs per source or partition. |
| **Compute** | Transform speed | More Spark executors, more Flink task managers, more parallel tasks in the orchestrator; auto-scaling clusters. |
| **Storage** | Capacity and read/write IOPS | More buckets/containers, partition count; for warehouses, more nodes or bigger warehouse size. |

Scale the **bottleneck** first: measure where time is spent (ingest, transform, or load) and add capacity there before over-provisioning the rest.

---

#### Horizontal vs vertical scaling

| | Horizontal (scale-out) | Vertical (scale-up) |
|--|------------------------|---------------------|
| **What** | Add more nodes/workers/partitions | Bigger CPU, memory, disk per node |
| **Pros** | No single-node limit, better fault tolerance, pay for what you use | Simpler ops, no distributed coordination |
| **Cons** | Coordination overhead, data distribution, more moving parts | Ceiling on single machine, single point of failure |
| **When** | Batch (Spark, EMR), streaming (Kafka consumers), warehouses (Redshift, Snowflake) | Small pipelines, single-node DBs, dev/test |

For data pipelines, **prefer horizontal**: use Spark, Flink, or managed services that add workers or partitions as load grows.

---

#### Partitioning for scale

- **Partition keys**: Choose columns that are often used in filters (e.g. `date`, `region`, `tenant_id`) so the engine can skip entire partitions (partition pruning).
- **Partition size**: Aim for **reasonably sized** partitions (e.g. 1–10 GB per partition in a lake, or 1 day per partition for event data). Too many tiny partitions → slow metadata and many small files; too few huge partitions → no parallelism and slow single-task runs.
- **Write path**: Write one partition (or partition range) per task where possible so jobs can run in parallel (e.g. one Airflow task per date partition).
- **Overwrites**: Use **partition-level overwrite** (replace only the partition(s) you processed) so runs are idempotent and don’t touch unrelated data.

---

#### Handling data skew

- **Skew** = some keys or partitions have much more data than others → a few tasks do most of the work and the rest sit idle.
- **Mitigations**:
  - **Salting**: Add a random suffix to the key (e.g. `user_id || '_' || rand(0, N)`) so heavy keys are spread across multiple partitions; aggregate again if needed.
  - **Two-phase aggregate**: First aggregate by (key + salt), then aggregate across salts to get final totals.
  - **Split large partitions**: For known hot keys, split into sub-partitions or process in separate jobs.
- **Monitor**: Watch task duration distribution; if a few tasks are much slower than the rest, investigate skew.

---

#### Autoscaling and elasticity

- **Batch**: Use **ephemeral clusters** (e.g. EMR, Databricks) that spin up for the job and shut down after; or serverless (Glue, Lambda) that scale with parallelism.
- **Streaming**: Scale **consumer count** with Kafka/Kinesis partitions (more partitions → more consumers); use **autoscaling** on Flink/Spark Streaming worker count based on lag or throughput.
- **Orchestration**: Limit **concurrent runs** (e.g. max N jobs per pipeline or per pool) so that a burst of triggers doesn’t overload shared resources.

---

#### Resource and performance tuning

- **Memory**: Give executors enough heap to avoid spills; tune Spark `memoryOverhead` and `executor.memory` (or equivalent) for your workload.
- **Parallelism**: Set **shuffle partitions** (Spark) or **parallelism** (Flink) to match cluster size (e.g. 2–4x number of cores); avoid too many (small tasks) or too few (underutilization).
- **Shuffle**: Reduce shuffle size by filtering and projecting early; use broadcast joins for small dimension tables; avoid huge skew in join keys.
- **I/O**: Use **columnar formats** (Parquet, ORC) and **predicate pushdown** so only needed columns and row groups are read; compress and partition for storage efficiency.
- **Cost**: Right-size clusters (don’t over-provision); use **spot/preemptible** for batch where acceptable; turn off or downsize dev/test when not in use.

---

#### Scaling checklist (interview-ready)

1. **Measure** where time is spent (ingest vs transform vs load) and where the bottleneck is.
2. **Scale the bottleneck**: more ingest connectors/partitions, more compute workers, or more storage/IOPS.
3. **Partition** data by a key that matches query patterns; keep partition sizes reasonable.
4. **Prefer horizontal scaling** (Spark, Flink, managed services) over single-node scale-up.
5. **Handle skew** (salting, two-phase agg, split hot keys) so no single task dominates runtime.
6. **Use incremental processing** where possible to reduce data scanned per run.
7. **Tune resources**: memory, parallelism, shuffle; use columnar formats and predicate pushdown.
8. **Use ephemeral or autoscaling** clusters so you don’t pay for idle capacity.

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
8. **Scalability**: What to scale (ingest/compute/storage), horizontal vs vertical, partitioning, skew handling, autoscaling, resource tuning.
9. **Docs & maintenance**: Catalog, runbooks, monitoring, and continuous improvement.

---

## 📚 Additional Resources

- [ETL Pipelines: 5 Key Components and 5 Critical Best Practices](https://dagster.io/guides/etl/etl-pipelines-5-key-components-and-5-critical-best-practices)
- [Data Pipeline Monitoring: Best Practices for Full Observability](https://www.prefect.io/blog/data-pipeline-monitoring-best-practices)
- [How to Enforce Data Quality at Every Stage](https://dagster.io/blog/how-to-enforce-data-quality-at-every-stage)
- [Data Pipeline Orchestration (Databricks)](https://www.databricks.com/resources/whitepaper/data-pipeline-orchestration)
- [Google Dataflow pipeline best practices](https://cloud.google.com/dataflow/docs/guides/pipeline-best-practices)
