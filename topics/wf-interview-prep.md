# Data Engineering Interview Prep — AWS-First, Production-Grade

Material for an **AWS shop**: **Topic 1 is AWS Glue**. **Topics 2–12** are **independent** (Python, SQL, architecture, governance, migration, orchestration) with **AWS services** where they matter.

Each section includes **depth**, **extra examples**, and **interview angles** (what panels probe, sample framing).

---

## How to answer design questions (generic order)

1. **Requirements** — volume, latency, SLAs, compliance, consumers, idempotency.  
2. **Architecture** — boundaries, environments, data zones, ownership.  
3. **Data flow** — sources, formats, partitioning, sinks, contracts.  
4. **AWS components** — Glue, EMR, Lambda, MWAA, Step Functions, S3, RDS, etc.  
5. **Code / config approach** — parameters, tests, schema strategy.  
6. **Best practices** — security, cost, observability.  
7. **Scaling & failure** — retries, DLQ, backfill, replay.  
8. **CI/CD** — artifacts, IaC, promotion, rollback.

---

# Topic 1 — AWS Glue (managed ETL)

**In one sentence:** Glue runs **PySpark/Scala** jobs (`glueetl`) and **Python shell** jobs, registers metadata in the **Glue Data Catalog**, and connects to data in **S3**, **JDBC** sources, and other AWS services.

### Interview angle (open with this)

> “Glue gives us managed Spark without running clusters 24/7. We use the **Data Catalog** so Athena and other engines see the same tables. For heavy transforms we use **Spark jobs**; for small JDBC pulls or scripts we might use **Python shell**. We treat **raw** as immutable and use **bookmarks** or **partitions** for incremental loads.”

### Components (deeper)

| Piece | Role | Example question |
|--------|------|------------------|
| **Data Catalog** | Hive-compatible metastore; tables/partitions | *How do Athena and Glue share metadata?* |
| **Crawler** | Infer schema from S3 | *Why not rely on crawlers alone?* |
| **glueetl job** | Distributed Spark | *When is Glue Spark overkill?* |
| **pythonshell** | Single-node; modest data | *Lambda vs pythonshell?* |
| **Connection** | JDBC + optional VPC | *How does Glue reach private RDS?* |
| **Job bookmark** | Tracks processed files/rows for incremental runs | *What breaks bookmarks?* |
| **Workflow / Trigger** | Schedule or chain jobs | *vs Step Functions?* |

### Simple scenario (walkthrough)

**Nightly** job: read **raw** JSON under `s3://raw/events/dt=2025-04-03/`, **dedupe** on `event_id`, write **Snappy Parquet** to `s3://curated/events/` with partition `dt`, register/update table `curated.events`.

### Second example — JDBC parallel read (interview favorite)

Large **RDS** table `orders`: use **parallel JDBC** so Spark reads multiple ranges at once.

```python
# PySpark — concept Glue uses under the hood for parallel reads
df = (
    spark.read.format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "orders")
    .option("user", user)
    .option("password", password)
    .option("driver", "org.postgresql.Driver")
    .option("partitionColumn", "order_id")  # numeric, evenly distributed ideal
    .option("lowerBound", "1")
    .option("upperBound", "50000000")
    .option("numPartitions", "16")
    .load()
)
```

**Talking point:** Pick a **partition column** that is **indexed** and roughly uniform; skewed keys → skewed tasks.

### Job bookmarks (when they work / break)

- **Work well:** Append-only S3 layout; new files or new folders per run.  
- **Break / surprise:** **Overwrite** same object key; **compaction** that rewrites paths the bookmark already “finished”; **late files** dropped into old `dt` prefix (you may need **watermark + reprocess** window).  
- **Late data:** Mention **idempotent** merge by key + **partition** re-run for specific `dt`, not only bookmark.

### Glue vs EMR (soundbite)

| Glue | EMR / EMR Serverless |
|------|----------------------|
| Less ops; good default for catalog-integrated batch | Custom AMIs, long-lived clusters, deeper Spark tuning |
| Glue Flex for cheaper windows | More knobs for exotic libs |

Say: *“We’d pick EMR if we need a **custom runtime**, **long-running** cluster, or **very specific** Spark tuning; Glue when we want **managed** jobs tied to the **Catalog** and **S3**.”*

### Production issues (expand)

- **Crawler drift** — string → bigint flip; **mitigation:** define tables via **DDL** / **Terraform**, use crawler for **discovery** only.  
- **Tiny files** — `repartition(n)` or `coalesce(n)` before write; target **~128–256 MB** objects.  
- **Wide IAM** — scope to `bucket/prefix` + **KMS** key for that bucket.  
- **Spark defaults** — e.g. `shuffle.partitions` may be wrong for your data size → tune with metrics.

### Optimizations (checklist)

- Partition **early**; **predicate pushdown** on `dt`, `region`.  
- **Column pruning** — select columns explicitly.  
- **Broadcast** small dimensions when join stats support it (watch memory).  
- **Glue 4.x** — align with supported Spark features; validate **connectors**.  
- **Cost** — Glue Flex, bookmarks, **avoid** full-table scans when incremental suffices.

### Code — Glue entry pattern (bookmarks + args)

```python
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

def main():
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    args = glueContext.getResolvedOptions(
        ["JOB_NAME", "SOURCE_PATH", "TARGET_PATH", "PROCESS_DATE"],
    )
    job.init(args["JOB_NAME"], args)

    # Enable job bookmark in job definition (--job-bookmark-option job-bookmark-enable)
    df = spark.read.json(f"{args['SOURCE_PATH']}/dt={args['PROCESS_DATE']}/")
    out = df.filter("event_id IS NOT NULL").dropDuplicates(["event_id"])
    out.write.mode("overwrite").partitionBy("dt").parquet(args["TARGET_PATH"])

    job.commit()

if __name__ == "__main__":
    main()
```

### Cross-questions (with angles)

- **EMR vs Glue?** — Control vs managed; catalog integration; team skills.  
- **Bookmarks + late data?** — Bookmarks aren’t a **business** late-arrival policy; add **reprocessing** by partition.  
- **Schema drift?** — Explicit schema, **registry**, CI on DDL, **merge** with care.  
- **VPC?** — Glue **connection** + **subnet** + **security groups**; S3 via **VPC endpoint** or NAT; **least privilege** IAM.

---

# Topic 2 — ETL pipeline design & optimization (Python, production-grade)

**In one sentence:** Treat ETL as **staged** pipelines with **clear contracts**, **idempotent** writes, **observability**, and **right-sized** compute (not every problem is Spark).

### Interview angle

> “I separate **extract**, **transform**, **load** into testable units. **Raw** is immutable; **curated** applies business rules. I make batches **idempotent** by partition or primary key so **retries** don’t double-count. I measure **freshness** and **row counts**, not just ‘job succeeded’.”

### Medallion-style layers (talk through)

| Layer | Holds | Typical rule |
|--------|--------|----------------|
| **Bronze / Raw** | As landed; append-only | No destructive edits |
| **Silver / Curated** | Cleaned, conformed types | Dedupe, standard keys |
| **Gold / Serving** | Aggregates, wide marts | BI / API contracts |

### Simple scenario

**Extract:** Partner drops CSV to S3. **Transform:** Validate rows, map to canonical schema. **Load:** Upsert into **curated** Parquet by `(business_key, dt)`.

### Idempotency (examples interviewers love)

**Same batch run twice** should not duplicate facts.

1. **Partition overwrite:** `INSERT OVERWRITE` / Spark `mode("overwrite")` for **one** `dt` partition only.  
2. **Merge / upsert:** `MERGE INTO` (warehouse) keyed by `id`.  
3. **Append with dedupe:** Insert to staging → `MERGE` to target, or `dropDuplicates` on **natural key** before append (know your **late-arriving** rules).

```python
# Illustrative: deterministic row key for dedupe in batch
def natural_key(row: dict) -> str:
    return f"{row['order_id']}|{row['line_id']}|{row['dt']}"
```

### Production issues

- **Monolith script** — can’t unit test; **split** `extract.py` / `transforms.py` / `load.py` (or packages).  
- **Silent schema change** — add **contract tests** on sample files in CI.  
- **Config in Git** wrong for prod — use **SSM** / **Secrets Manager** + **env-specific** buckets from args.

### Optimizations

- **Pure functions** for transforms → **pytest** without Spark.  
- **Right engine:** Lambda for MB-scale; **Fargate** for medium; **Glue/EMR** for TB+.  
- **Observability:** emit **metrics** (`rows_in`, `rows_out`, `null_rate`) to CloudWatch.

### Code — structure + testable transform

```python
# transforms.py — pure, easy to test
def normalize_email(v: str | None) -> str | None:
    if not v:
        return None
    return v.strip().lower()

def enrich_row(raw: dict, process_date: str) -> dict:
    return {
        "user_id": raw["user_id"],
        "email": normalize_email(raw.get("email")),
        "dt": process_date,
    }
```

```python
# test_transforms.py
def test_normalize_email():
    assert normalize_email("  A@B.COM ") == "a@b.com"
    assert normalize_email(None) is None
```

### Cross-questions

- **Idempotent daily batch?** — Overwrite partition `dt` or merge on **business key**; **watermark** optional.  
- **Quality before or after curated?** — **Light** checks at ingest (reject poison); **heavy** rules on **curated** before **gold**.  
- **Version logic vs data?** — Git tags for **code**; **partition** + **snapshot** tables for **data** history.

---

# Topic 3 — Parallelism: multiprocessing vs threading; errors, logging, retries

**In one sentence:** **CPU-bound** Python → **multiprocessing** (or native libs); **I/O-bound** → **threads** or **asyncio**; **retries** need **limits**, **jitter**, and **idempotency** for side effects.

### Interview angle

> “The **GIL** means threads don’t parallelize CPU-heavy Python bytecode. For parallel CPU work I use **multiprocessing** or **push work to Spark / native code**. For S3 and HTTP I use **thread pools** or **async** with bounded concurrency. Retries use **exponential backoff with jitter** so we don’t stampede the API.”

### GIL (short)

One thread holds the **Global Interpreter Lock** for CPU work in CPython → multiple threads **interleave**, not parallelize CPU. **I/O** releases the GIL, so threads help **network/disk** wait time.

### When to use what

| Workload | Typical choice |
|----------|----------------|
| Many HTTP downloads | `ThreadPoolExecutor`, `asyncio`, or Lambda fan-out |
| Heavy pandas/numpy CPU on chunks | `ProcessPoolExecutor` or Spark |
| boto3 S3 copy many keys | Thread pool + tuned **TransferConfig** |

### Simple scenario

**10k** presigned URLs → download → upload to S3: **thread pool** (I/O bound). **Resize images** with Pillow on large images: **process pool** or **offload** to batch.

### Retries + duplicate side effects

**Problem:** Retry delivers **two** S3 writes or **two** API `POST`s.

**Mitigations:** **Idempotency keys** (API supports `Idempotency-Key` header); **write** to deterministic S3 key `.../order_id=123/part-000.parquet` and **overwrite**; **dedupe** downstream; **SQS FIFO** + dedup window where applicable.

### Production issues

- **Threads + CPU pandas** — no speedup; use **vectorization** or **Spark**.  
- **Infinite retry** — cap attempts; **DLQ** after threshold.  
- **Unstructured logs** — use **JSON** + `run_id` for CloudWatch **metric filters**.

### Code — ThreadPoolExecutor + bounded workers

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_one(client, bucket: str, key: str) -> str:
    # ... return etag or version id
    return "ok"

def download_many(client, bucket: str, keys: list[str], max_workers: int = 16):
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(download_one, client, bucket, k): k for k in keys}
        for fut in as_completed(futs):
            k = futs[fut]
            fut.result()  # raises if failed
```

### Code — structured logging (JSON-friendly fields)

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        return json.dumps(payload)

# logger.addHandler(handler); record with extra_fields={'run_id': '...'}
```

### Cross-questions

- **Why threads don’t speed CPU Python?** — **GIL**; use **processes** or **native/Spark**.  
- **Lambda vs EC2 job?** — **Volume**, **duration**, **memory**, **VPC** cold start; Lambda for **short** parallel **shards**; **long** unified job on **Batch/Fargate/EMR**.  
- **Duplicate retry?** — **Idempotent** keys, **deterministic** writes, **merge** semantics.

---

# Topic 4 — API ingestion & file processing

**In one sentence:** APIs need **respect for rate limits**, **pagination**, **checkpoints**, and **secrets rotation**; files need **size limits**, **format validation**, and **malware** process where policy requires.

### Interview angle

> “I treat the API as an **unreliable** dependency: **backoff**, **circuit breaker** mindset, **checkpoint** in DynamoDB so we can resume. For files I **land raw** to S3, **scan** if required, then **parse** in a job that can scale.”

### AWS angle

- **API Gateway + Lambda** — sync HTTP; **SQS** to absorb spikes.  
- **AppFlow** — Salesforce, Slack, etc. → S3 (low code when fit).  
- **S3** — landing; **EventBridge** / **notifications** trigger **Lambda** or **Step Functions**.  
- **Transfer Family** — SFTP/FTPS into S3.  
- **Secrets Manager** — rotate DB/API secrets; **IAM roles** for AWS APIs.

### Pagination patterns

| Style | Pros | Cons |
|--------|------|------|
| **Offset/limit** | Simple | Slow/deep pages; **inconsistent** if data shifts |
| **Cursor / keyset** | Stable for live feeds | Store **cursor** per shard |
| **Time windows** | Good for logs | Clock skew; **overlap** windows for safety |

```python
# Cursor pagination (sketch)
def iter_all(base_url: str, headers: dict, start: str | None = None):
    cursor = start
    while True:
        r = requests.get(base_url, headers=headers, params={"cursor": cursor}, timeout=60)
        r.raise_for_status()
        body = r.json()
        for item in body["items"]:
            yield item
        cursor = body.get("next_cursor")
        if not cursor:
            break
```

### Checkpoint in DynamoDB (concept)

```text
PK: ingestion_name#shard_id
SK: CHECKPOINT
attrs: last_cursor, last_success_ts, rows_ingested
```

**Interview:** *“On failure we **don’t** restart from zero; we **resume** from `last_cursor`.”*

### File processing

- **Stream** large files — don’t `read()` entire file in Lambda if it can exceed memory.  
- **CSV** — delimiter/quote issues; **bad rows** to quarantine.  
- **Zip bombs** — size caps, **scan** in isolated service.  
- **Avro/Parquet** — schema from **registry** / **Glue**.

### Production issues

- **429** — respect **Retry-After**; **reduce** `max_workers`.  
- **Duplicate pages** — **idempotent** sink by natural key.  
- **Lambda 15 min** — **Step Functions** loop + **checkpoint**, or **ECS** worker.

### Cross-questions

- **Schema change?** — **Additive** columns; **registry**; **quarantine** unknown fields.  
- **Long pagination?** — **Step Functions** state machine + **Lambda** steps; or **ECS** long runner.  
- **Secrets?** — **Secrets Manager** + **IAM**; never in env vars in repo.

---

# Topic 5 — Data validation & schema enforcement

**In one sentence:** Enforce **contracts** at boundaries: **row** validation (types), **dataset** checks (row counts, null %), and **evolution** rules (additive vs breaking).

### Interview angle

> “**Row-level** validation catches bad payloads early. **Aggregate** checks catch **silent** failures—zero rows, 50% drop in volume. I separate **fatal** (fail job) from **quarantine** (bad records to DLQ bucket/prefix).”

### AWS angle

- **Glue Data Quality** — declarative rules in jobs.  
- **Schema Registry** — compatibility **BACKWARD** for consumers.  
- **Lake Formation** — **access**, not row content validation.

### Validation tiers

| Tier | Example | Action |
|------|---------|--------|
| Row | `amount >= 0`, UUID format | Drop row or quarantine |
| Batch | `rows > 0`, `error_rate < 1%` | Fail job, page on-call |
| Cross-batch | vs yesterday’s count ± threshold | Alert only |

### Pydantic + batch stats

```python
from pydantic import BaseModel, Field, ValidationError
from uuid import UUID

class Event(BaseModel):
    event_id: UUID
    amount: float = Field(ge=0)

def validate_batch(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    good, bad = [], []
    for r in rows:
        try:
            good.append(Event.model_validate(r).model_dump())
        except ValidationError:
            bad.append(r)
    return good, bad
```

### Schema evolution (say this clearly)

- **Backward compatible:** New **optional** column; old readers ignore.  
- **Breaking:** Rename column, change `int` → `string` without migration — coordinate **consumers**.

### Production issues

- **Validate only in BI** — too late.  
- **Brittle rules** — `len(email) > 3` rejects valid edge cases.  
- **0 rows green** — always assert **min row count** or **freshness**.

### Cross-questions

- **Backward compatible example?** — Add `promo_code` optional; writers populate; old Athena queries unchanged.  
- **CI for validators?** — **pytest** with **golden** bad/good JSON fixtures.  
- **Quarantine vs fail?** — **Quarantine** when **partial** bad data expected; **fail** when **batch** integrity required (financial close).

---

# Topic 6 — Complex joins, window functions, CTEs

**In one sentence:** **CTEs** structure readable SQL; **windows** avoid **self-joins** for rankings and running metrics; **join** hygiene prevents **Cartesian** explosions.

### Interview angle

> “I **filter early** in CTEs. For **windows**, I always set **PARTITION BY** deliberately—without it, the window is over the whole table. I know **`ROW_NUMBER`** vs **`RANK`** for dedupe vs ties.”

### CTE example — clean steps

```sql
WITH daily AS (
  SELECT customer_id, dt, SUM(amount) AS revenue
  FROM curated.orders
  WHERE dt BETWEEN DATE '2025-04-01' AND DATE '2025-04-07'
  GROUP BY 1, 2
),
ranked AS (
  SELECT
    customer_id,
    dt,
    revenue,
    RANK() OVER (PARTITION BY dt ORDER BY revenue DESC) AS rev_rank
  FROM daily
)
SELECT * FROM ranked WHERE rev_rank <= 10;
```

### Window functions — differences (memorize)

| Function | Behavior |
|----------|----------|
| `ROW_NUMBER()` | Unique 1,2,3… per partition; arbitrary tie break |
| `RANK()` | Ties get same rank; **gaps** after ties |
| `DENSE_RANK()` | Ties same rank; **no gaps** |
| `LAG(col,1)` / `LEAD` | Prior/next row in partition order |

### Anti-join / not exists pattern

“Customers who **never** ordered product X”:

```sql
SELECT c.customer_id
FROM curated.customers c
LEFT JOIN curated.orders o
  ON c.customer_id = o.customer_id
 AND o.product_id = 'X'
WHERE o.order_id IS NULL;
```

Or: `WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE ...)`.

### Sessionization (concept)

**Gap > 30 min** between events → new session: cumulative sum of “new session” flags (classic interview pattern).

```sql
WITH ordered AS (
  SELECT user_id, event_ts,
    LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) AS prev_ts
  FROM curated.events
  WHERE dt = DATE '2025-04-01'
),
flags AS (
  SELECT *,
    CASE WHEN prev_ts IS NULL OR event_ts > prev_ts + INTERVAL '30' MINUTE
         THEN 1 ELSE 0 END AS new_session
  FROM ordered
)
SELECT user_id, event_ts,
  SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_ts) AS session_id
FROM flags;
```

### Athena vs Redshift (joins)

- **Athena:** Pay per **data scanned** → **partition** + **columnar** + **limit columns**.  
- **Redshift:** **DISTKEY** on large fact to align with big dimension; **SORTKEY** for filter columns.

### Cross-questions

- **ROW_NUMBER vs RANK?** — Dedupe use **`ROW_NUMBER() ... WHERE rn=1`**; leaderboards with ties use **RANK**.  
- **Athena join cost?** — **Scan**-driven; **partition** both sides if possible.

---

# Topic 7 — Indexing strategy & performance tuning

**In one sentence:** **OLTP** indexes speed point lookups; **analytics** systems use **distribution**, **sort order**, **partitioning**, and **columnar** layout—not “index everything.”

### Interview angle

> “On **Postgres/RDS** I’d verify with **`EXPLAIN (ANALYZE, BUFFERS)`** and add **composite** indexes matching **filter + order** columns. On **Redshift** I think **DISTKEY** and **SORTKEY**, not B-tree indexes. On **Athena** there are **no** row indexes—only **partition pruning** and **file format**.”

### RDS / Aurora (example)

Query: `WHERE status = 'OPEN' AND created_at > '2025-04-01' ORDER BY created_at`.

- Candidate index: `(status, created_at)` **or** partial index `WHERE status = 'OPEN'` if highly selective.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE status = 'OPEN' AND created_at > TIMESTAMP '2025-04-01'
ORDER BY created_at
LIMIT 100;
```

**Watch:** **Write** amplification and **autovacuum** on churny tables.

### Redshift (concept)

- **DISTKEY** on large fact’s **join key** to **dimension** → **co-located** joins.  
- **SORTKEY** on **filter** columns (e.g. `dt`) → **zone map** pruning.  
- **Bad:** Random **DISTKEY** on high-cardinality UUID → **no** co-location.

### DynamoDB (“indexing”)

Access patterns drive **PK/SK**; **GSI** for alternate lookups. **Avoid** hot partitions (uneven key distribution).

### Athena

- **Partition** `dt`, `hour` if queries always filter.  
- **Parquet** + **column projection**; avoid `SELECT *`.

### Production issues

- **Too many indexes** — slow writes, planner confusion.  
- **Redshift** — **wrong** DISTKEY → massive **network** shuffle.  
- **Missing** `ANALYZE** / **stats** — bad plans.

### Cross-questions

- **When not to index?** — Small table, write-heavy, low-selectivity column, or **covered** by better composite.  
- **Redshift join spills?** — **DIST/SORT**, **fewer** columns, **pre-aggregate**, **workload management (WLM)**.

---

# Topic 8 — Star vs snowflake schema design

**In one sentence:** **Star** = fact + **denormalized** dimensions (simpler joins); **Snowflake** = **normalized** dimensions (less redundancy, more joins).

### Interview angle

> “In **Kimball**-style marts I default to **star** for usability. I **snowflake** only when we **reuse** hierarchies across many dimensions or **storage** of denorm duplicates is costly. **Grain** of the fact table is non-negotiable—one row per **line item** vs **order** must be explicit.”

### Star example (textual)

`fact_sales(order_sk, date_sk, product_sk, customer_sk, qty, amount)`  
`dim_product(product_sk, name, category)` — category denormalized in star.

### Snowflake twist

`dim_store` → `dim_region` → `dim_country` as separate tables → **more joins**, **less** duplicate region names.

### SCD Type 2 (must know)

**Slowly Changing Dimension Type 2:** Keep **history** when `customer` address changes.

Columns: `customer_sk` **surrogate**, `natural_id`, `effective_start`, `effective_end`, `is_current`.

```sql
SELECT * FROM dim_customer
WHERE natural_id = 'C123'
  AND DATE '2025-04-01' BETWEEN effective_start AND COALESCE(effective_end, DATE '9999-12-31');
```

### Degenerate dimensions

`order_id` on **fact** line table—no separate dim if not attribute-rich.

### Production issues

- **Over-snowflake** in Athena — many small joins; **denorm** judiciously for query patterns.  
- **No SCD2** — wrong **historical** revenue by region.

### Cross-questions

- **SCD2 dates?** — `effective_start` / `effective_end` / `is_current`.  
- **Fact grain?** — “**One row per order line per day**” (example)—every metric must **match** that grain.

---

# Topic 9 — End-to-end pipeline architecture

**In one sentence:** E2E spans **ingest → store → process → serve → observe**, with **ownership**, **SLAs**, and **failure modes** documented.

### Interview angle

> “End-to-end I care about **data contracts** between teams, **SLAs** on **freshness**, and **runbooks** for **replay** from **raw**. I’d draw **S3 zones**, **Glue jobs**, **Catalog**, **Athena/Redshift** consumers, and **CloudWatch** alarms on **business metrics**, not only CPU.”

### Reference flow (AWS)

1. **Ingest:** DMS / Kinesis / SFTP → **S3 raw**.  
2. **Process:** **Glue** curated Parquet.  
3. **Catalog:** **Glue** tables.  
4. **Serve:** **Athena** views; **QuickSight**; optional **Redshift** for low-latency BI.  
5. **Orchestrate:** **MWAA** or **Step Functions**.  
6. **Observe:** **CloudWatch** metrics, **logs**, **PagerDuty** integration.

### SLIs / SLOs (impress)

- **Freshness:** `max(dt)` in table **lag** vs wall clock < **24h**.  
- **Completeness:** row count **within X%** of prior day.  
- **Error rate:** validation failures < **Y%**.

### PII masking — where?

- Often **mask** in **curated** or **gold** for broad access; **raw** locked down. Say: *“Depends on **regulatory** read access to raw; default is **restrict raw**, **mask** for general analytics.”*

### DR (short)

- **S3** cross-region replication for critical buckets; **Glue** jobs redeployed via **IaC**; **RPO/RTO** with business.

### Cross-questions

- **PII?** — Layer + **LF** column permissions / **masked views**.  
- **DR?** — **Backup**, **replication**, **replay** from raw.

---

# Topic 10 — RBAC, data governance & multi-layer architecture

**In one sentence:** **RBAC** assigns **roles** to **actions** on **resources**; **governance** adds **classification**, **lineage**, **audit**; **layers** separate **trust zones**.

### Interview angle

> “**Humans** get **SSO**-federated roles; **jobs** get **service roles** with **least privilege** on **prefix**. **Lake Formation** can enforce **column** access for **Athena** users when we need **finer** than IAM path-only. **CloudTrail** audits **who called** `GetObject` / `StartQueryExecution`.”

### IAM example (principle)

Data engineer role: `s3:ListBucket` on bucket; `s3:GetObject` only `arn:.../curated/*`; **no** `raw/*` if unnecessary.

### Lake Formation (when)

- **Column/row** level for **Athena/Glue** consumers; central **LF-DB** administrator.  
- **Tradeoff:** Operational overhead; must align **IAM** + **LF** + **S3**.

### Layers (repeat with governance)

| Layer | Trust | Typical policy |
|--------|--------|----------------|
| Raw | Low (messy) | Locked; ingestion + break-glass |
| Curated | Medium–high | ETL roles; approved analysts |
| Serving | High for BI | Aggregates; PII minimized |

### Cross-questions

- **IAM vs LF?** — IAM for **coarse** S3 paths; **LF** for **table/column** in **lake** analytics.  
- **Audit column read?** — **CloudTrail** for API; **LF** audit logs; **Athena** workgroup logging.

---

# Topic 11 — On-premises → AWS migration

**In one sentence:** Use **discovery**, **pilot**, **network**, then **bulk** or **CDC**, validate **continuously**, and **cut over** with **rollback**.

### Interview angle

> “I’d start with **inventory**: schemas, **volume**, **downtime** tolerance, **compliance**. **DMS** for **CDC** to **RDS** or **S3**; **Snowball** if **network** is the bottleneck. **Cutover** only after **row counts**, **checksums**, and **lag** SLAs are green.”

### Phases

1. **Assess** — dependencies, **6 Rs** (rehost, replatform, refactor…).  
2. **Network** — **Direct Connect** / **VPN**; security review.  
3. **Pilot** — one **schema** or **read replica** path.  
4. **Sync** — **DMS full + CDC** or **bulk** + one-time cut.  
5. **Validate** — counts, **spot** checksums, **application** tests.  
6. **Cutover** — **DNS**, connection strings, **freeze** window.

### DMS sketch

- **Source:** Oracle / SQL Server / Postgres.  
- **Target:** **Aurora** / **S3** (Parquet for lake).  
- **Replication instance** in VPC; **security groups** allow source.

### Production issues

- **Firewall** / **TLS** to source.  
- **LOB** / **binary** mapping.  
- **Cutover** **underestimated** — need **rollback** DB snapshot.

### Cross-questions

- **Minimize cutover risk?** — **Rehearse**, **read-only** dry run, **keep** on-prem **read** path until validated, **feature flag** app routing.  
- **Bulk vs CDC?** — **Bulk** simpler for one-time; **CDC** for **near-zero** downtime **sync**.

---

# Topic 12 — Data pipeline orchestration

**In one sentence:** Orchestration coordinates **dependencies**, **retries**, **backfills**, **SLAs**, and **human** escalation—not just **schedule**.

### Interview angle

> “I’d use **MWAA** if we need **rich** Python operators and **ecosystem**; **Step Functions** for **serverless** **state machines** with **native** AWS integrations. **EventBridge** for **decoupled** **event** triggers. **Glue Workflows** when **everything** is **Glue**.”

### Compare (talking points)

| Tool | Strength | Caveat |
|------|----------|--------|
| **MWAA** | Complex DAGs, sensors, backfill | Ops, cost, upgrades |
| **Step Functions** | Durable execution, visual | ASL complexity at scale |
| **Glue Workflow** | Simple Glue DAG | Less flexible |
| **EventBridge** | Rules, schedules | Not a full DAG alone |

### Step Functions pattern (concept)

`StartGlueJob` → `Wait` / poll → `Choice` on success → `SNS` on fail. **Map** state for **parallel** `dt` list.

### Airflow pattern (concept)

```python
# Pseudocode — interview: describe DAG structure, not memorize API
with DAG("daily_curated", schedule="@daily") as dag:
    ingest = GlueJobOperator(task_id="ingest", job_name="...")
    quality = PythonOperator(task_id="quality", python_callable=run_checks)
    ingest >> quality
```

### Backfill idempotently

Pass **`start_dt`**, **`end_dt`** as **job params**; **overwrite** each **partition**; **Step Functions Map** over dates.

### Production issues

- **Cron only** — hidden **dependencies**.  
- **No backfill** — manual pain.  
- **One mega-DAG** — **blast radius**.

### Cross-questions

- **Airflow vs Step Functions?** — **Complexity** of DAG vs **managed** states; team **skills**.  
- **Backfill 30 days?** — **Parameterized** job + **parallel** dates + **idempotent** writes.

---

## CI/CD & quality (deeper bite)

- **Artifact:** `s3://artifacts/glue/<git-sha>/job.py` + `common.zip`; **Glue job** points to that prefix.  
- **IaC:** Terraform **aws_glue_job** + **IAM** role **scoped** to prefix.  
- **Tests:** **pytest** on **pure** code; **dev** **StartJobRun** smoke with **tiny** partition.  
- **Rollback:** Repoint job to **`git-sha-1`** or **Terraform** `artifact_version` variable.

---

## Quick recap — “What service when?”

| Need | Often use |
|------|-----------|
| Managed Spark ETL | **Glue** / **EMR** |
| SQL over lake | **Athena** |
| Warehouse | **Redshift** |
| OLTP migration | **DMS** → **Aurora** |
| Orchestration | **MWAA**, **Step Functions** |
| Events | **EventBridge**, **SQS** |

---

## Prep pattern (use in every interview story)

**Situation → Constraint → What you built (AWS pieces) → Failure/issue → Fix → Metric (time/cost/quality).**

Rehearse **one story per topic** so you can go deep on follow-ups without rambling.
