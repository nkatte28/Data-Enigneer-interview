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

### Components — answers (interview + code)

**Q: How do Athena and Glue share metadata?**  
**A:** They both use the **same** **AWS Glue Data Catalog**. A table you register in Glue (DDL, API, or crawler) is what Athena resolves when you run `SELECT` against `database.table`. Partitions in the catalog are used for **partition pruning** in Athena. No separate copy of schema—**one source of truth**.

```sql
-- Athena reads table definition from Glue Catalog
SELECT COUNT(*) FROM curated.events WHERE dt = DATE '2025-04-03';
```

---

**Q: Why not rely on crawlers alone?**  
**A:** Crawlers **infer** types from sampled data. That can **change** run-to-run (e.g. all-null column inferred as string, later becomes int), breaking downstream SQL. **Production:** define tables with **explicit DDL** (or Terraform `aws_glue_catalog_table`), use crawlers only for **discovery** or non-critical zones.

```sql
-- Prefer explicit CTAS or DDL over crawler-only for critical tables
CREATE TABLE curated.events (
  event_id STRING,
  dt DATE,
  amount DECIMAL(18,2)
)
PARTITIONED BY (dt)
STORED AS PARQUET
LOCATION 's3://curated/events/';
```

---

**Q: When is Glue Spark overkill?**  
**A:** When data fits in **one machine** comfortably and work is **light** (filter a few MB, small JDBC extract under typical Lambda or single-node time). Use **Lambda**, **Glue Python shell**, or **Fargate** instead—**less cost** and **no cluster startup**. Spark pays off for **large** S3/parallel JDBC/**shuffle** workloads.

```python
# Heuristic: tiny input → avoid Spark if team allows
import os
if os.path.getsize("input.csv") < 50 * 1024 * 1024:
    ...  # pandas / polars on single node
else:
    ...  # Spark / Glue ETL
```

---

**Q: Lambda vs Glue Python shell?**  
**A:** **Lambda:** event-driven, **15-minute** max, **10 GB** RAM cap, great for **per-file** S3 triggers. **Glue Python shell:** **longer** runs (check current Glue quotas), **Glue connection** to VPC JDBC, built-in Glue job metrics—better for **scheduled** “small ETL” that **exceeds Lambda limits** or needs **Glue’s** JDBC/VPC integration without Spark.

```text
Choose Lambda:  S3 event → transform 1 file → put result
Choose pythonshell:  nightly JDBC 2 GB table → S3, runs 45 min, VPC to RDS
```

---

**Q: How does Glue reach private RDS?**  
**A:** Create a **Glue connection** (JDBC URL + subnet + **security groups**). The job role needs `glue:GetConnection`. Glue creates an **ENI** in your subnets so traffic stays private; RDS SG must **allow** the Glue connection’s SG on the DB port. S3 access is typically via **VPC endpoint** or **NAT**.

```text
Glue job → uses Connection → ENI in private subnet → SG allows 5432 → RDS
```

---

**Q: What breaks bookmarks?**  
**A:** Bookmarks track **what was already processed**. They break when: (1) you **overwrite** the same S3 **key** (bookmark thinks it’s done); (2) **compaction** rewrites files; (3) **late files** land under an old prefix the bookmark skipped. **Mitigation:** append-only keys, **reprocess** by `dt` with **idempotent** writes, or **reset** bookmark after logic change (with understanding of reprocessing scope).

```python
# Idempotent partition re-run (does not rely on bookmark for that day)
spark.read.parquet(f"{raw}/dt={process_date}/").write.mode("overwrite").partitionBy("dt").parquet(curated)
```

---

**Q: Glue Workflow vs Step Functions?**  
**A:** **Glue Workflow:** chains **Glue** jobs, crawlers, triggers—**simple**, native console. **Step Functions:** **any** AWS API—Lambda, Glue, Batch, **wait for human**, **parallel** maps, **long** state machine—use when orchestration crosses **many services** or needs **complex branching/retries** beyond Glue-only.

```text
Glue Workflow:  crawl → job A → job B (all Glue)
Step Functions:  Event → Lambda validate → Map over dates → Glue → SNS alert
```

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

### Cross-questions — answers

**Q: EMR vs Glue?**  
**A:** **Glue:** fully managed job execution, **Data Catalog** integration, pay per **DPU** run time, less ops. **EMR:** you choose **cluster** shape, **custom AMIs**, **long-lived** clusters for iterative work, **finer** Spark tuning. Pick **EMR** when you need **control** or **non-standard** stack; **Glue** for **catalog-centric** lake ETL with **minimal** cluster management.

```text
Glue:     script on S3 → StartJobRun → done
EMR:      create cluster → step → optionally keep cluster for notebooks
```

---

**Q: Bookmarks + late data?**  
**A:** Bookmarks track **processed files/offsets**—they don’t encode **business rules** for lateness. If events arrive **after** the bookmark advanced, **re-run** the affected **partition(s)** (`dt`) with **idempotent** merge/dedupe. Optionally maintain a **watermark** table (`last_processed_ts`) for **API** sources.

```python
# Reprocess one day idempotently (example pattern)
def merge_partition(spark, dt: str):
    new_df = spark.read.parquet(f"{raw}/dt={dt}/")
    # MERGE in Delta/Iceberg, or overwrite partition after dropDuplicates(keys)
    new_df.dropDuplicates(["event_id"]).write.mode("overwrite").partitionBy("dt").parquet(f"{curated}/")
```

---

**Q: Schema drift—how do you prevent surprises?**  
**A:** (1) **Explicit** table DDL in Git; (2) **Glue Schema Registry** or **Avro/JSON** compatibility **BACKWARD**; (3) CI tests on **sample** files; (4) Spark `mergeSchema` only where you **accept** extra columns and cast safely.

```python
# Spark: controlled merge + cast
df = spark.read.option("mergeSchema", "true").parquet(path)
df = df.withColumn("amount", col("amount").cast("decimal(18,2)"))
```

---

**Q: How do you secure Glue in a VPC?**  
**A:** **Glue connection** attaches subnets/SGs; job runs with access to **private** JDBC. **IAM** role: `s3:GetObject`/`PutObject` only on required prefixes, `kms:Decrypt` for bucket keys, `glue:GetConnection`. **S3:** VPC **gateway endpoint**; avoid routing **large** data through NAT unnecessarily. **Least privilege**—no `Resource: "*"` on S3.

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::company-curated-prod/events/*"
}
```

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

### Cross-questions — answers

**Q: What does idempotent daily batch mean—how do you implement it?**  
**A:** Running the job **twice** for the same **business day** does **not** duplicate rows. Implement by: **overwrite** only that day’s **partition** (`dt`); or **`MERGE`** / upsert on **natural key**; or **truncate-and-load** staging then swap. Spark example for partition overwrite:

```python
out = transform(raw_df)
out.write.mode("overwrite").option("partitionOverwriteMode", "dynamic").partitionBy("dt").parquet("s3://curated/facts/")
```

---

**Q: Where do you put data quality checks—before or after curated?**  
**A:** **Both**, with different strictness. **Ingest:** reject **poison** (malformed JSON, impossible types) → quarantine or DLQ. **Curated:** **business rules** (referential sanity, aggregates vs source). **Gold:** **reporting** checks (revenue ties to finance). Say **defense in depth**, not one gate only.

```python
# Ingest: hard fail tiny sample
assert len(rows) > 0, "empty batch"
bad_rate = len(bad) / max(len(rows), 1)
if bad_rate > 0.01:
    raise RuntimeError("too many bad rows")
```

---

**Q: How do you version pipeline logic vs data?**  
**A:** **Logic:** Git tags / semver on deployable artifact (`job.py` hash in S3). **Data:** **time partitions** (`dt`), **snapshot** tables (`orders_as_of_2025q1`), or **SCD2** dimensions. Auditors care **which code version** produced **which** partition.

```text
s3://artifacts/glue/v1.2.3/job.py  →  writes  s3://curated/sales/dt=2025-04-01/
```

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

### Cross-questions — answers

**Q: Why don’t threads speed up CPU-bound Python?**  
**A:** **CPython** uses a **Global Interpreter Lock (GIL)**: only one thread runs Python bytecode at a time for CPU work. Threads still help **I/O wait** (releases GIL during I/O). For **CPU** parallelism use **`multiprocessing`**, **native** libs (NumPy calls C), or **Spark**.

```python
# CPU-bound: processes (simplified)
from concurrent.futures import ProcessPoolExecutor

def heavy(x: int) -> int:
    return sum(i * i for i in range(x))

with ProcessPoolExecutor() as ex:
    list(ex.map(heavy, range(1000, 1100)))
```

---

**Q: Lambda concurrent invocations vs one big EC2/Batch job?**  
**A:** **Lambda:** **sharded** work (e.g. **one S3 prefix per invocation**), **15 min** cap, **automatic** scale, pay per ms. **Batch/Fargate/EC2:** **single** long job, **hours** of runtime, **predictable** resources, **VPC** without per-invocation cold start pain. Choose Lambda when **embarrassingly parallel** and **short**; choose Batch when **single** long pipeline or **>15 min**.

```text
10k small files:  Lambda map (capped concurrency) or Step Functions Map
10 TB single scan:  Glue / EMR / Batch job
```

---

**Q: How do you avoid duplicate side effects when retries run twice?**  
**A:** **Idempotency keys** on APIs (`Idempotency-Key` header); **deterministic** S3 keys and **overwrite**; **MERGE** in warehouse; **dedupe** by primary key downstream; message systems **at-least-once** → consumer **dedupes**.

```python
import hashlib

def deterministic_s3_key(order_id: str, dt: str) -> str:
    h = hashlib.sha256(f"{order_id}|{dt}".encode()).hexdigest()[:16]
    return f"curated/orders/dt={dt}/order_id={order_id}/{h}.parquet"
```

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

### Cross-questions — answers

**Q: How do you handle API schema changes without dropping events?**  
**A:** Treat unknown fields as **optional**; land **raw JSON** as-is; **parse** known columns in curated step. Use **schema registry** with **backward-compatible** rules; **version** API responses (`schema_version` column). **Quarantine** records that fail **required** field checks.

```python
def parse_event(raw: dict) -> dict:
    return {
        "event_id": raw["event_id"],
        "amount": raw.get("amount", 0.0),
        "promo_code": raw.get("promo_code"),  # new optional field — old events OK
    }
```

---

**Q: Lambda timeout vs Step Functions for long pagination?**  
**A:** **Lambda** alone is capped at **15 minutes**. **Pattern:** Step Functions **loop**—each Lambda invocation processes **one page**, writes **checkpoint** to DynamoDB, returns `next_cursor` to Step Functions, which **invokes** Lambda again until **no cursor**. For **hours** of streaming pagination, **ECS/Fargate** or **Glue Python shell** may be simpler.

```text
Step Functions:  Choice(cursor exists?) → Lambda(fetch page) → Update DynamoDB → loop
```

---

**Q: Where do you store secrets?**  
**A:** **AWS Secrets Manager** (rotation) or **SSM Parameter Store** (SecureString). Glue/Lambda/ECS get secrets via **IAM** at runtime—**never** commit secrets to Git. Reference by **ARN** in job config.

```python
import boto3

def get_api_key(secret_arn: str) -> str:
    sm = boto3.client("secretsmanager", region_name="us-east-1")
    resp = sm.get_secret_value(SecretId=secret_arn)
    import json
    return json.loads(resp["SecretString"])["api_key"]
```

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

### Cross-questions — answers

**Q: Give a backward-compatible schema change example.**  
**A:** Add a new **optional** column `promo_code STRING` to events. **Old** producers omit it → **NULL** in queries. **Old** Athena `SELECT event_id, amount` still works. **Breaking** would be **renaming** `amount` → `amt` without dual-write period.

```sql
-- After adding column in Glue/DDL — old files still readable with NULL for new column
SELECT event_id, amount, promo_code FROM curated.events WHERE dt = DATE '2025-04-01';
```

---

**Q: How do you test validators in CI?**  
**A:** **pytest** with **fixture files**: `good.jsonl`, `bad_missing_id.jsonl`, `bad_negative_amount.jsonl`. Assert **counts** of good/bad and **error messages**. Run on every PR.

```python
# tests/test_validate.py
import json
from pathlib import Path

def test_rejects_negative_amount():
    from pipeline.validate import validate_batch
    rows = [{"event_id": "550e8400-e29b-41d4-a716-446655440000", "amount": -1.0}]
    good, bad = validate_batch(rows)
    assert len(good) == 0 and len(bad) == 1
```

---

**Q: Quarantine vs fail the job—when?**  
**A:** **Fail** when the **batch** cannot be trusted (financial totals, more than 1% bad rows, **zero** rows). **Quarantine** when **some** bad rows are expected (messy vendor) but **most** rows are valid—write bad to `s3://quarantine/...` and **alert** if rate spikes.

```python
if len(good) == 0:
    raise RuntimeError("entire batch invalid — fail")
if len(bad) / len(rows) > 0.01:
    raise RuntimeError("too many bad rows — fail")
write_quarantine(bad)
```

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

### Cross-questions — answers

**Q: ROW_NUMBER vs RANK—when use which?**  
**A:** **`ROW_NUMBER()`** assigns **unique** integers 1..N in the partition—use for **deduplication** (“keep one row per key”). **`RANK()`** gives **same** rank to ties and **skips** numbers after a tie (1,2,2,4)—use for **leaderboards** where ties matter. **`DENSE_RANK()`** ties but **no gaps** (1,2,2,3).

```sql
-- Dedupe: one row per customer_id (pick arbitrary row among ties)
WITH x AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
  FROM curated.customers
)
SELECT * FROM x WHERE rn = 1;

-- Leaderboard with ties
SELECT customer_id, revenue, RANK() OVER (ORDER BY revenue DESC) AS rnk FROM daily_revenue;
```

---

**Q: Athena join cost—what drives it?**  
**A:** **Bytes scanned** in S3 (Parquet column + partition pruning). **No** row indexes. Reduce cost: **partition** both tables on **join/filter** columns (`dt`), **column projection** (`SELECT` needed cols only), **bucket** or **sort** data if team uses it, avoid **broadcast** hints that hide huge builds—**filter before join**.

```sql
-- Good: prune partitions first
SELECT f.order_id, d.name
FROM fact_orders f
JOIN dim_customer d ON f.customer_id = d.customer_id
WHERE f.dt BETWEEN DATE '2025-04-01' AND DATE '2025-04-07'
  AND d.dt = DATE '2025-04-07';  -- if dim is partitioned; adjust to model
```

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

### Cross-questions — answers

**Q: When would you NOT add an index?**  
**A:** **Tiny** tables (sequential scan is cheap). **Write-heavy** tables where every extra index slows **INSERT/UPDATE**. **Low-selectivity** columns (e.g. boolean `is_active`). **Redundant** index already **covered** by composite leading prefix. Always confirm with **`EXPLAIN`** and **workload** (read vs write ratio).

```sql
-- Before adding index: baseline plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = $1;
```

---

**Q: Redshift join spills to disk—what do you tune?**  
**A:** **DISTKEY** alignment so fact and large dimension **co-locate**; **SORTKEY** on **filter** columns; **reduce** selected columns; **pre-aggregate** to smaller fact; increase **work_mem**-like settings via **WLM** queue memory; break query into **CTEs** materialized to temp tables if needed (tradeoffs).

```sql
-- Illustrative: smaller right-hand side via pre-aggregate
WITH daily AS (
  SELECT customer_id, dt, SUM(amount) AS amt FROM fact_sales GROUP BY 1, 2
)
SELECT * FROM daily d JOIN dim_customer c ON d.customer_id = c.id;
```

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

### Cross-questions — answers

**Q: What is SCD Type 2 and where do effective dates live?**  
**A:** **SCD2** preserves **history** when a dimension attribute changes (e.g. customer **region**). Each change adds a **new row** with new **surrogate key**; **natural_id** ties versions. Columns: **`effective_start`**, **`effective_end`** (or `NULL` / high date = open), **`is_current`**. Queries use **`BETWEEN`** on **as-of** date.

```sql
SELECT customer_sk, region
FROM dim_customer
WHERE natural_id = 'C123'
  AND DATE '2025-04-01' BETWEEN effective_start AND COALESCE(effective_end, DATE '9999-12-31');
```

---

**Q: What is fact table grain?**  
**A:** **One row per** a single **business event** at the **lowest** level you store—e.g. **one row per order line**, not per order, if line-level discounts matter. **Every measure** on that table must be **additive** or **semi-additive** consistently with that grain. Mixing grains in one fact causes **double-counting** in rollups.

```text
Grain: one row per (order_id, line_id) — revenue_line = qty * unit_price
Wrong:  same fact also stores order-level shipping duplicated on every line — document allocation rules
```

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

### Cross-questions — answers

**Q: Where do you implement PII masking?**  
**A:** Often **not** in raw (immutable audit copy); **mask/hash/tokenize** in **curated** or **gold** for broad access. **Lake Formation** column-level permissions, **Athena** **views** with `sha2(email)`, or **Dynamic Data Masking** patterns in warehouse. **Raw** access: **break-glass** role + **audit**.

```sql
-- Athena view: expose masked email for analysts
CREATE VIEW curated.customer_safe AS
SELECT
  customer_id,
  CASE WHEN current_user IN ('role_privileged') THEN email ELSE regexp_replace(email, '(.*)@', '***@') END AS email
FROM curated.customer_pii;
```

---

**Q: How do you approach disaster recovery for the data lake?**  
**A:** **S3** cross-region **replication** for critical buckets; **versioning** + **lifecycle**; **Glue** job definitions from **IaC** (rebuild in new region). **RPO/RTO** with business. **Replay** pipeline from **raw** if curated lost but raw intact.

```text
RPO: how much data can we lose (e.g. 1 hour of raw)
RTO: how fast restore (e.g. 4 hours to flip reads to secondary region)
```

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

### Cross-questions — answers

**Q: IAM vs Lake Formation—when use which?**  
**A:** **IAM** on **S3** is **prefix/object** level—good for **engineering** roles and **jobs**. **Lake Formation** adds **Glue Catalog**–aware **table/column/row** policies for **Athena/Glue** users without mapping every path. Use **LF** when **analysts** need **different columns** from same table; use **IAM-only** when simple **bucket separation** is enough.

```text
IAM:     role glue-etl → s3://lake/curated/sales/*
LF:      analyst group → SELECT on sales except columns (ssn, cc_number)
```

---

**Q: How do you audit who read a column in Athena?**  
**A:** **CloudTrail** logs **`StartQueryExecution`** (who ran what), **Athena** workgroup **query results** to S3 with **logging** enabled; **LF** **audit** logs for access checks. True **cell-level** “who read column X” is **hard**—combine **query text** logs + **table/column** grants + **least privilege**. For strict needs, **masked views** + **no direct** base table access.

```text
CloudTrail:  user ARN, time, StartQueryExecution
S3 logs:     query result location per workgroup
LF:          Grant/revoke audit trail
```

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

### Cross-questions — answers

**Q: How do you minimize cutover risk?**  
**A:** **Rehearse** cutover in lower env; **dual-run** (compare counts/checksums); **read-only** freeze window; **DMS CDC** until **replication lag** is under the agreed threshold (e.g. seconds); **rollback** plan: **DNS** back, **DB snapshot** restore, **feature flag** to old connection string. **Validate** app smoke tests before flipping writes.

```text
Pre-cutover:  row counts match, checksum sample, latency OK
Cutover:      stop writes → final sync → point apps → verify → enable writes
Rollback:     documented decision tree if checksum fails
```

---

**Q: Bulk load vs CDC—tradeoffs?**  
**A:** **Bulk** (one-time `COPY`/export/import): **simpler**, good for **initial** load or **small** DB; **downtime** or **read-only** window often needed for final consistency. **CDC** (DMS, Debezium): **continuous** sync, **lower** cutover downtime, **more** moving parts (replication slot, **transformation** of changes). Many migrations: **bulk** for baseline + **CDC** for catch-up.

```text
Bulk:     mysqldump → S3 → Glue → OR DMS full load only
CDC:      DMS full load + ongoing replication until cutover
```

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

### Cross-questions — answers

**Q: Airflow (MWAA) vs Step Functions—how do you choose?**  
**A:** **MWAA:** Python **operators**, huge **ecosystem** (DB, Spark, sensors), **backfill** via CLI/UI, team knows Airflow. **Ops:** upgrades, cost, VPC. **Step Functions:** **serverless**, **native** AWS service integrations, **per-state** retry/visual **ASL**, great for **Lambda/Glue** chains and **human approval** steps. **Simpler** ops but **ASL** can grow large. Pick **MWAA** for **complex** data DAGs + Python; **Step Functions** for **event-driven** **serverless** pipelines.

```json
{
  "Comment": "Minimal Step Functions → Glue → Choice",
  "StartAt": "RunGlue",
  "States": {
    "RunGlue": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": { "JobName": "curate_daily" },
      "End": true
    }
  }
}
```

---

**Q: How do you backfill 30 days idempotently?**  
**A:** Parameterize job with **`start_dt`**, **`end_dt`**. For each `dt`, **overwrite** that **partition** or **MERGE** with **natural keys**. **Parallelize** with **Step Functions Map** or **Airflow** `for` with **pool** limit. **Idempotency:** same `dt` run twice = same result.

```python
# Airflow-style idea: mapped tasks per date
from datetime import date, timedelta

def backfill_dates(start: date, end: date):
    d = start
    while d <= end:
        run_glue(process_date=d.isoformat())  # each run overwrites dt partition
        d += timedelta(days=1)
```

---

## CI/CD & quality (deeper bite)

- **Artifact:** `s3://artifacts/glue/<git-sha>/job.py` + `common.zip`; **Glue job** points to that prefix.  
- **IaC:** Terraform **aws_glue_job** + **IAM** role **scoped** to prefix.  
- **Tests:** **pytest** on **pure** code; **dev** **StartJobRun** smoke with **tiny** partition.  
- **Rollback:** Repoint job to **`git-sha-1`** or **Terraform** `artifact_version` variable.

### CI/CD — questions & answers

**Q: How do you package and deploy a Glue job?**  
**A:** Build **versioned** artifacts in CI: upload `job.py` + `dependencies.zip` (or **wheel**) to **S3**; **Terraform/CloudFormation** sets `script_location` and `--extra-py-files`. **Promote** same **hash** across dev → qa → prod with **different** parameters/IAM.

```bash
# CI (concept)
aws s3 cp glue_jobs/ingest/job.py s3://artifacts/glue/${GIT_SHA}/ingest/job.py
aws s3 cp build/deps.zip s3://artifacts/glue/${GIT_SHA}/deps.zip
terraform apply -var="glue_script_hash=${GIT_SHA}"
```

---

**Q: How do you validate deployment before prod?**  
**A:** **Smoke** `StartJobRun` in **QA** with **small** `PROCESS_DATE` or **limit**; assert **SUCCEEDED** and **row counts** greater than zero; optional **Athena** query on output path. **Automate** in pipeline after **apply**.

```python
import boto3, time

def wait_job(job_name: str, run_id: str) -> str:
    glue = boto3.client("glue")
    while True:
        r = glue.get_job_run(JobName=job_name, RunId=run_id)["JobRun"]
        s = r["JobRunState"]
        if s in ("SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"):
            return s
        time.sleep(10)
```

---

**Q: Rollback strategy?**  
**A:** Keep **previous** S3 artifact prefix; **Terraform** `artifact_version` variable **revert** to last good **git tag**; **Glue job** default args point to known-good script. **Data** rollback: **re-run** idempotent job for affected **partitions** from **raw**, not “delete S3” blindly.

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
