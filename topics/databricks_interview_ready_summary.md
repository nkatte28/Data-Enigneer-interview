# Databricks Interview-Ready Summary

This document summarizes the Databricks topics covered end-to-end, with concise interview-ready explanations and corrections on areas where wording matters.

---

# 1. Lakehouse Architecture

A simple answer:

> “I usually start by understanding source systems, data volume, velocity, formats, arrival frequency, latency SLA, and consumption patterns. Based on that, I decide where batch or streaming is appropriate. I typically use a Bronze-Silver-Gold architecture.”

```text
Sources
  ↓
Bronze
raw / append-oriented ingestion
  ↓
Silver
clean / dedupe / CDC / trusted entities
  ↓
Gold
facts / dimensions / aggregates
  ↓
BI / ML / downstream consumers
```

## Bronze

- Raw landing layer.
- Minimal transformation.
- Usually append-oriented.
- Preserve source fidelity.
- Add metadata like ingestion timestamp/source file.
- Capture rescued/corrupt data.

## Silver

- Clean, standardized, trusted.
- Type casting, deduplication, DQ.
- CDC processing.
- `MERGE` where updates/deletes are required.
- Reusable business entities.

## Gold

- Business consumption layer.
- Star schemas.
- Facts/dimensions.
- Aggregates/KPIs/data marts.
- Append or `MERGE` depending on table behavior.

Important line:

> “A streaming source does not mean every downstream layer must be streaming. Processing mode should be driven by SLA.”

---

# 2. Delta Tables

Best short answer:

> “Delta Lake adds transactional capabilities on top of distributed Parquet files. It gives us ACID transactions, UPDATE, DELETE, MERGE, time travel, schema enforcement/evolution, Change Data Feed, and transaction history through the Delta log.”

## Physical Structure

```text
Delta Table
   |
   +-- Parquet data files
   |
   +-- _delta_log
```

Actual rows are in Parquet files.

`_delta_log` contains actions such as:

```text
commitInfo
add
remove
metaData
protocol
```

Important correction:

> Delta log does not contain the actual data rows.

## ACID

- **Atomicity** — whole transaction succeeds or none of it does.
- **Consistency** — successful transactions leave data in a valid state.
- **Isolation** — concurrent operations do not corrupt one another.
- **Durability** — committed changes remain committed.

## Delta Checkpoint

Do not confuse it with streaming checkpointing.

```text
Delta checkpoint
→ summarized transaction-log state
→ faster table snapshot reconstruction
```

It does **not** create time travel.

## Time Travel

Versions are logical snapshots.

```text
V1 → A B C
V2 → A D C
V3 → A D E
```

Files A/C can be reused across versions.

Therefore:

> 8 versions does not mean 8 complete copies of the table.

## Schema Enforcement

Delta protects the existing table schema.

```text
Target:
customer_id BIGINT

Incoming:
customer_id = incompatible value
```

The write can fail.

Important line:

> “Schema enforcement protects the table; schema evolution explicitly allows supported changes.”

Schema evolution example:

```python
.option("mergeSchema", "true")
```

---

# 3. Delta MERGE

Basic upsert:

```sql
MERGE INTO target t
USING source s
ON t.customer_id = s.customer_id

WHEN MATCHED THEN
  UPDATE SET *

WHEN NOT MATCHED THEN
  INSERT *
```

PySpark:

```python
(
    target.alias("t")
    .merge(
        source.alias("s"),
        "t.customer_id = s.customer_id"
    )
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)
```

Important:

> `MERGE` itself is not SCD Type 1. The logic you build determines Type 1 or Type 2.

## SCD Type 1

Overwrite the old value.

```text
Raleigh
→ Charlotte
```

## SCD Type 2

Expire old row + insert new row.

```text
101 | Raleigh   | false
101 | Charlotte | true
```

Single-MERGE trick:

```text
merge_key = customer_id
→ MATCHED → expire old row

merge_key = NULL
→ NOT MATCHED → insert new version
```

That is a good interview-level SCD2 explanation.

---

# 4. Delta Optimization

Organize this into four buckets:

```text
1. File size
2. Data layout
3. Automatic maintenance
4. Cleanup
```

## OPTIMIZE

```sql
OPTIMIZE sales;
```

Purpose:

> Compact many small Parquet files into fewer larger files.

It reduces file-open and task-scheduling overhead.

## Z-ORDER

```sql
OPTIMIZE sales
ZORDER BY (customer_id);
```

Do **not** call it indexing.

Say:

> “Z-ORDER physically colocates similar values to improve data skipping.”

## Liquid Clustering

```sql
CLUSTER BY (customer_id, sale_date)
```

Best explanation:

> “Liquid clustering defines a flexible physical data layout. It groups similar values so file-level statistics become more selective and data skipping can eliminate more files.”

Backend:

```text
Liquid clustering
       ↓
better-organized Parquet files
       ↓
better min/max separation
       ↓
data skipping
       ↓
less data scanned
```

It also works well with high-cardinality columns where normal partitioning would be problematic.

Important correction:

> Liquid clustering does not mean OPTIMIZE disappears.

Without Predictive Optimization:

```text
CLUSTER BY
→ defines layout

OPTIMIZE
→ physically applies compaction + clustering
```

## Predictive Optimization

Think:

```text
Databricks decides WHEN
to run maintenance
```

It can automate:

```text
OPTIMIZE
VACUUM
ANALYZE
```

There is compute cost associated with it.

## VACUUM

```sql
VACUUM sales;
```

Deletes obsolete physical files outside the retention period.

Important:

> VACUUM can reduce how far back time travel is possible.

---

# 5. Auto Loader

Best interview answer:

> “Auto Loader is Databricks’ scalable incremental file-ingestion mechanism for cloud object storage such as S3, ADLS, and GCS.”

Typical pipeline:

```text
Cloud files
   ↓
Auto Loader
   ↓
Bronze Delta
```

Important capabilities:

- incremental file discovery
- checkpoint-based progress
- schema inference
- schema evolution
- rescued data
- corrupt-record handling
- rate control
- scalable file discovery

Important options:

```python
cloudFiles.format
cloudFiles.schemaLocation
cloudFiles.schemaEvolutionMode
cloudFiles.schemaHints
cloudFiles.maxFilesPerTrigger
cloudFiles.maxBytesPerTrigger
rescuedDataColumn
```

## Rescued vs Corrupt

```text
_rescued_data
→ parsed record but schema mismatch/unexpected fields

_corrupt_record
→ record cannot be parsed correctly
```

## Target Schema Evolution

Auto Loader side:

```python
.option(
    "cloudFiles.schemaEvolutionMode",
    "addNewColumns"
)
```

Delta target side:

```python
.option("mergeSchema", "true")
```

Think:

```text
Auto Loader evolves DataFrame
        ↓
mergeSchema lets Delta target evolve
```

## Scaling Auto Loader

Main levers:

```text
file-event discovery
maxFilesPerTrigger
maxBytesPerTrigger
Spark compute
source file sizing
backlog monitoring
```

Monitor:

```text
numFilesOutstanding
numBytesOutstanding
```

---

# 6. Structured Streaming

Mental model:

> “Structured Streaming treats a stream as a continuously growing table and processes incremental changes, usually using micro-batches.”

## Checkpoint

Streaming checkpoint:

```text
progress
offsets
state
recovery information
```

Different from Delta-log checkpoint.

## Output Modes

```text
Append
→ new finalized rows

Update
→ changed results

Complete
→ full result every trigger
```

## Watermark

Best explanation:

> “Watermarking uses event time to bound how long Spark keeps state for late-arriving data.”

Example:

```python
.withWatermark("event_time", "10 minutes")
```

Used heavily for:

```text
window aggregations
stateful processing
stream-stream joins
late data
```

Important distinction:

```text
Output mode
→ what Spark emits

Watermark
→ how long Spark keeps state
```

---

# 7. CDC and CDF

CDF exposes:

```text
_change_type
_commit_version
_commit_timestamp
```

Change types include things like:

```text
insert
delete
update_preimage
update_postimage
```

Important distinction:

```text
_commit_version / timestamp
→ when Delta committed the change

event_timestamp / sequence
→ when business event happened
```

For late-arriving records:

> Use commit metadata to identify newly available changes; use business timestamps/sequence numbers to order business history correctly.

---

# 8. Unity Catalog

Best summary:

> “Unity Catalog gives centralized governance across catalogs, schemas, tables, views, functions, volumes, and other data assets.”

Hierarchy:

```text
Catalog
  ↓
Schema
  ↓
Table / View / Function
```

## RBAC

Use groups + grants.

```text
Users
  ↓
Groups
  ↓
Privileges
  ↓
Catalog / Schema / Table
```

Typical grants:

```sql
GRANT USE CATALOG
ON CATALOG retail_prod
TO `sales_analysts`;

GRANT USE SCHEMA
ON SCHEMA retail_prod.gold
TO `sales_analysts`;

GRANT SELECT
ON SCHEMA retail_prod.gold
TO `sales_analysts`;
```

Best line:

> “I prefer group-based permissions instead of direct user grants because they are easier to manage and audit.”

## Row-Level Security

UDF returns Boolean.

```sql
CREATE FUNCTION security.region_filter(region STRING)
RETURN
  CASE
    WHEN is_account_group_member('east_team')
         AND region = 'EAST'
      THEN TRUE
    ELSE FALSE
  END;
```

Apply:

```sql
ALTER TABLE sales.orders
SET ROW FILTER security.region_filter
ON (region);
```

## Column Masking

UDF returns displayed value.

```sql
CREATE FUNCTION security.mask_ssn(ssn STRING)
RETURN
  CASE
    WHEN is_account_group_member('hr_team')
      THEN ssn
    ELSE '***-**-****'
  END;
```

Apply:

```sql
ALTER TABLE customers
ALTER COLUMN ssn
SET MASK security.mask_ssn;
```

Remember:

```text
Row filter
→ which rows you see

Column mask
→ what value you see
```

## ABAC

```text
RBAC
→ access based on role/group

ABAC
→ policy based on attributes/tags
```

Useful at scale when hundreds of tables/columns need similar security policies.

## Other Unity Catalog Features

Know these:

```text
lineage
auditability
metadata/discovery
governed tags
external locations
storage credentials
volumes
Delta Sharing
```

## Delta Sharing

Good short answer:

> “Delta Sharing provides secure governed sharing of data with users or organizations without requiring us to copy the dataset into another system.”

---

# 9. Workflows / Jobs Orchestration

Think:

```text
Job
  ↓
Tasks
  ↓
Dependencies
  ↓
DAG
```

Example:

```text
Bronze
  ↓
Silver
  ↓
Gold
  ↓
DQ
```

Know:

```text
task dependencies
parameters
retries
timeouts
repair runs
notifications
schedule/triggers
compute configuration
```

## DABs

Declarative Automation Bundles:

```text
Git
 ↓
YAML definitions
 ↓
validate
 ↓
deploy
 ↓
run
```

Main commands:

```bash
databricks bundle init

databricks bundle validate -t dev

databricks bundle deploy -t dev

databricks bundle run -t dev retail_job
```

Schedule goes into job configuration:

```yaml
schedule:
  quartz_cron_expression: "0 0 2 * * ?"
  timezone_id: "America/New_York"
  pause_status: "UNPAUSED"
```

Good line:

> “DABs give me version-controlled, repeatable Dev/Test/Prod deployment of Databricks resources.”

---

# 10. Compute Architecture

Three major concepts:

```text
Interactive / all-purpose
→ development and debugging

Jobs compute
→ production scheduled workloads

Serverless
→ Databricks-managed compute
```

## Job Clusters

Ephemeral:

```text
start
→ run job
→ terminate
```

Better than leaving interactive clusters running for production.

## Serverless

Advantages:

```text
fast provisioning
automatic scaling
less infrastructure management
less idle-capacity management
```

## Node Families

On AWS, remember:

```text
M
→ general purpose

C
→ compute optimized

R
→ memory optimized

I
→ storage optimized
```

Example:

```text
r6i.2xlarge
```

means roughly:

```text
R → memory optimized
6 → generation
i → Intel variant
2xlarge → size
```

In job YAML:

```yaml
new_cluster:
  node_type_id: r6i.2xlarge

  autoscale:
    min_workers: 2
    max_workers: 10

  runtime_engine: PHOTON
```

## Choosing Nodes

```text
CPU saturated
→ compute optimized

OOM / shuffle spill
→ memory optimized

cache / heavy local I/O
→ storage optimized

unsure
→ general purpose first
```

Important:

> Do not compensate for poor Spark design by blindly adding nodes.

---

# 11. Photon

Know this sentence:

> “Photon is Databricks’ vectorized execution engine that accelerates supported SQL and DataFrame workloads and can improve price/performance.”

Don't say:

> Photon automatically makes everything faster.

Say:

> Evaluate workload suitability and overall price/performance.

---

# 12. Package Management on Serverless

Quick/ad hoc:

```python
%pip install ...
```

Better project-level approach:

```text
pyproject.toml
→ declares dependencies

uv.lock
→ locks exact resolved versions

serverless environment
→ installs/synchronizes them
```

Good line:

> “For production, I prefer Git-controlled dependency definitions instead of scattering `%pip install` commands across notebooks.”

---

# 13. Cost Optimization

Best framework:

> **right compute + right size + efficient code + no idle resources + monitor spending**

Main points:

```text
Use jobs/serverless for production
Avoid persistent interactive compute
Autoscale where workload varies
Use auto-termination
Choose appropriate node family
Use spot where interruption is acceptable
Optimize Delta file layout
Reduce shuffle/skew
Use broadcast joins when appropriate
Evaluate Photon
Monitor billing
Tag resources
Set budgets/alerts
```

Important principle:

> **Optimize total workload cost, not DBU price alone.**

Example:

```text
small cluster × 90 minutes
```

can cost more than:

```text
larger cluster × 15 minutes
```

if the latter finishes efficiently.

---

# 14. Areas Where You Should Be Especially Precise in Interviews

These are the places where people commonly make technically incorrect statements.

**Do not say:** “Z-ORDER is an index.”  
**Say:** “Z-ORDER improves physical locality and data skipping.”

**Do not say:** “Liquid clustering removes the need for OPTIMIZE.”  
**Say:** “Liquid clustering defines the layout; OPTIMIZE applies it, while Predictive Optimization can automate maintenance.”

**Do not say:** “Delta checkpoint enables time travel.”  
**Say:** “Delta checkpoint accelerates log reconstruction; transaction history plus retained files enable time travel.”

**Do not say:** “CDF handles late data automatically.”  
**Say:** “CDF tells me newly committed changes; business timestamps/sequence numbers determine event ordering.”

**Do not say:** “Bronze is always CDC.”  
**Say:** “Bronze preserves raw source data/events and is commonly append-oriented.”

**Do not say:** “Gold always uses MERGE.”  
**Say:** “MERGE is appropriate when Gold needs updates/deletes; immutable facts may simply append.”

**Do not say:** “Serverless is always cheaper.”  
**Say:** “Serverless reduces operational and idle-capacity overhead; total cost depends on workload.”

---

# 15. Overall Interview Storyline

If someone asks you to design a Databricks platform, a strong answer structure is:

> “I first understand source systems, volume, velocity, data formats, business SLAs, and consumption requirements. Then I choose batch or streaming ingestion and land raw data into Bronze, typically using Auto Loader for cloud files or CDC/native connectors for databases. Silver handles cleansing, deduplication, data quality, CDC, and MERGE logic, while Gold provides dimensional models and business-ready aggregates. I use Delta Lake for ACID transactions, schema enforcement/evolution, time travel, CDF, and efficient DML. For performance I manage file size and layout using OPTIMIZE, liquid clustering, data skipping, and predictive optimization. Unity Catalog provides RBAC, row filters, column masking, lineage, auditability, storage governance, and sharing. Workflows/DABs handle orchestration and CI/CD, and I select jobs or serverless compute based on workload characteristics. Finally, I monitor quality, reliability, SLAs, and cost through observability, billing data, tagging, and alerts.”

That is the level of answer that shows you understand **Databricks as a platform**, not just individual features.
